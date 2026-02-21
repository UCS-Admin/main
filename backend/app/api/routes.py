from datetime import datetime, timezone
from pathlib import Path
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.entities import (
    AdmissionApplication,
    AIInsight,
    ApplicationStatus,
    AssociateCommission,
    AssociateLead,
    CollegeProfile,
    Difficulty,
    Institution,
    Option,
    PaperQuestion,
    PaperTemplate,
    PastPaper,
    Question,
    QuestionSource,
    QuestionType,
    RankingSnapshot,
    StudentDocument,
    StudentProgress,
    Test,
    TestAnswer,
    User,
    UserRole,
    VerificationTask,
)
from app.schemas.admission import ApplicationIn, ApplicationStatusIn, LeadIn, RankingIn
from app.schemas.common import (
    QuestionIn,
    QuestionOut,
    TemplateIn,
    TemplateOut,
    TestAnswerIn,
    TestStartIn,
    TestSubmitOut,
    TokenOut,
    UserCreate,
    UserLogin,
)
from app.services.analytics_service import student_analytics
from app.services.extraction_service import ensure_upload_dir, extract_pdf_text, infer_blueprint_from_text, split_question_blocks
from app.services.generator_service import generate_paper
from app.services.pdf_service import create_paper_pdf

router = APIRouter()


@router.get("/")
def landing():
    return {
        "name": "EPC Digital Admission + Question Paper Practice Platform",
        "modules": ["Student", "College", "Associate", "Admin", "AI", "Question Paper"],
    }


@router.post("/auth/register", response_model=TokenOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        institution_id=payload.institution_id,
    )
    db.add(user)
    db.commit()
    return TokenOut(access_token=create_access_token(payload.email))


@router.post("/auth/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(user.email))


@router.get("/dashboards/student")
def student_dashboard(user: User = Depends(require_roles(UserRole.STUDENT)), db: Session = Depends(get_db)):
    apps = db.query(AdmissionApplication).filter(AdmissionApplication.student_id == user.id).all()
    recent = db.query(PastPaper).order_by(PastPaper.id.desc()).limit(10).all()
    return {
        "epc_card": {"id": f"EPC-{user.id:05d}", "qr_payload": user.email},
        "admission_status": [{"college_id": a.institution_id, "status": a.status.value} for a in apps],
        "question_paper_practice": [{"paper_id": p.id, "title": p.title, "year": p.year} for p in recent],
    }


@router.get("/dashboards/college")
def college_dashboard(user: User = Depends(require_roles(UserRole.COLLEGE, UserRole.ADMIN)), db: Session = Depends(get_db)):
    institution_id = user.institution_id or 0
    total = db.query(AdmissionApplication).filter(AdmissionApplication.institution_id == institution_id).count()
    pending = db.query(AdmissionApplication).filter(
        AdmissionApplication.institution_id == institution_id,
        AdmissionApplication.status == ApplicationStatus.PENDING,
    ).count()
    return {"total_applications": total, "pending_verifications": pending}


@router.get("/dashboards/associate")
def associate_dashboard(user: User = Depends(require_roles(UserRole.ASSOCIATE)), db: Session = Depends(get_db)):
    leads = db.query(AssociateLead).filter(AssociateLead.associate_id == user.id).count()
    earned = db.query(func.coalesce(func.sum(AssociateCommission.amount), 0)).filter(AssociateCommission.associate_id == user.id).scalar()
    return {"total_leads": leads, "earnings_summary": earned}


@router.get("/dashboards/admin")
def admin_dashboard(_: User = Depends(require_roles(UserRole.ADMIN)), db: Session = Depends(get_db)):
    return {
        "total_students": db.query(User).filter(User.role == UserRole.STUDENT).count(),
        "total_colleges": db.query(Institution).count(),
        "total_associates": db.query(User).filter(User.role == UserRole.ASSOCIATE).count(),
        "verification_pending": db.query(VerificationTask).filter(VerificationTask.status == "PENDING").count(),
    }


@router.post("/applications")
def apply_college(payload: ApplicationIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.STUDENT))):
    app = AdmissionApplication(student_id=user.id, institution_id=payload.institution_id, course=payload.course)
    db.add(app)
    db.commit()
    db.refresh(app)
    return {"application_id": app.id, "status": app.status.value}


@router.get("/applications/me")
def my_applications(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.STUDENT))):
    apps = db.query(AdmissionApplication).filter(AdmissionApplication.student_id == user.id).all()
    return [{"id": a.id, "institution_id": a.institution_id, "status": a.status.value, "remarks": a.remarks} for a in apps]


@router.patch("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    payload: ApplicationStatusIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.COLLEGE, UserRole.ADMIN)),
):
    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = ApplicationStatus(payload.status)
    app.remarks = payload.remarks
    db.commit()
    return {"updated": True}


@router.post("/associates/leads")
def add_lead(payload: LeadIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ASSOCIATE))):
    lead = AssociateLead(associate_id=user.id, student_id=payload.student_id, institution_id=payload.institution_id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"lead_id": lead.id}


@router.post("/admin/rankings")
def upsert_ranking(payload: RankingIn, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN))):
    row = RankingSnapshot(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"saved": True}


@router.get("/colleges/search")
def college_search(city: str | None = None, course: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Institution)
    if city:
        query = query.filter(Institution.city.ilike(f"%{city}%"))
    rows = query.limit(100).all()
    result = []
    for r in rows:
        profile = db.query(CollegeProfile).filter(CollegeProfile.institution_id == r.id).first()
        if course and profile and profile.courses and course not in " ".join(profile.courses):
            continue
        result.append({"id": r.id, "name": r.name, "city": r.city, "rankings": profile.rankings if profile else {}})
    return result


@router.post("/sources/upload")
def upload_source(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER)),
):
    upload_dir = ensure_upload_dir()
    file_path = upload_dir / file.filename
    with file_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    source = QuestionSource(uploaded_by=user.id, file_path=str(file_path), extraction_status="UPLOADED")
    db.add(source)
    db.commit()
    db.refresh(source)
    return {"id": source.id, "file_path": source.file_path}


@router.post("/sources/{source_id}/extract")
def extract_source(source_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    source = db.query(QuestionSource).filter(QuestionSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    text, scanned = extract_pdf_text(source.file_path)
    blocks = split_question_blocks(text)
    source.extracted_text = text
    source.scanned = scanned
    source.extraction_status = "EXTRACTED"
    db.commit()
    return {"source_id": source.id, "scanned": scanned, "question_blocks": blocks[:50]}


@router.post("/admin/past-papers/upload")
def upload_past_paper(
    title: str,
    subject_id: int,
    grade: int,
    year: int | None = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    upload_dir = ensure_upload_dir()
    file_path = upload_dir / f"past_{datetime.now().timestamp()}_{file.filename}"
    with file_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    paper = PastPaper(title=title, subject_id=subject_id, grade=grade, year=year, file_path=str(file_path), uploaded_by=user.id)
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return {"paper_id": paper.id}


@router.post("/admin/past-papers/{paper_id}/ingest")
def ingest_past_paper(paper_id: int, db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN))):
    paper = db.query(PastPaper).filter(PastPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Past paper not found")
    text, _ = extract_pdf_text(paper.file_path)
    blocks = split_question_blocks(text)
    paper.extracted_blueprint = infer_blueprint_from_text(text)
    for block in blocks[:30]:
        q_type = QuestionType.MCQ if "(a)" in block or "option" in block.lower() else QuestionType.SHORT
        db.add(
            Question(
                subject_id=paper.subject_id,
                grade=paper.grade,
                year=paper.year,
                type=q_type,
                text=block[:1200],
                marks=1 if q_type == QuestionType.MCQ else 3,
                difficulty=Difficulty.MEDIUM,
                verified=True,
                created_by=1,
            )
        )
    paper.processed = True
    db.commit()
    return {"processed": True, "blueprint": paper.extracted_blueprint}


@router.get("/students/practice/papers")
def list_practice_papers(db: Session = Depends(get_db), _: User = Depends(require_roles(UserRole.STUDENT))):
    papers = db.query(PastPaper).filter(PastPaper.processed.is_(True)).order_by(PastPaper.year.desc().nullslast()).limit(10).all()
    return [{"paper_id": p.id, "title": p.title, "year": p.year, "grade": p.grade} for p in papers]


@router.post("/students/practice/generate-from-paper/{paper_id}")
def generate_similar_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.STUDENT, UserRole.ADMIN)),
):
    paper = db.query(PastPaper).filter(PastPaper.id == paper_id, PastPaper.processed.is_(True)).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper unavailable")
    ai_note = AIInsight(question_id=None, insight_type="SIMILAR_PAPER", content=f"Generated similar paper from base paper {paper_id}", approved=True)
    db.add(ai_note)
    db.commit()
    tpl = db.query(PaperTemplate).filter(PaperTemplate.subject_id == paper.subject_id, PaperTemplate.grade == paper.grade).first()
    if not tpl:
        tpl = PaperTemplate(title=f"AI Template from {paper.title}", grade=paper.grade, subject_id=paper.subject_id, blueprint=paper.extracted_blueprint or infer_blueprint_from_text(""), created_by=user.id)
        db.add(tpl)
        db.commit()
        db.refresh(tpl)
    generated = generate_paper(db, tpl.id, user.id, avoid_repeat_days=30)
    return {"paper_id": generated.id}


@router.post("/questions", response_model=QuestionOut)
def create_question(payload: QuestionIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    question = Question(**payload.model_dump(exclude={"options"}), created_by=user.id)
    db.add(question)
    db.flush()
    for opt in payload.options:
        db.add(Option(question_id=question.id, **opt.model_dump()))
    db.commit()
    db.refresh(question)
    return question


@router.get("/questions", response_model=list[QuestionOut])
def list_questions(
    db: Session = Depends(get_db),
    grade: int | None = Query(default=None),
    subject_id: int | None = Query(default=None),
    difficulty: Difficulty | None = Query(default=None),
    qtype: QuestionType | None = Query(default=None),
    verified: bool | None = Query(default=None),
):
    query = db.query(Question)
    if grade:
        query = query.filter(Question.grade == grade)
    if subject_id:
        query = query.filter(Question.subject_id == subject_id)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if qtype:
        query = query.filter(Question.type == qtype)
    if verified is not None:
        query = query.filter(Question.verified == verified)
    return query.all()




@router.get("/questions/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Not found")
    return question


@router.put("/questions/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, payload: QuestionIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in payload.model_dump(exclude={"options"}).items():
        setattr(question, key, value)
    db.query(Option).filter(Option.question_id == question.id).delete()
    for opt in payload.options:
        db.add(Option(question_id=question.id, **opt.model_dump()))
    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(question)
    db.commit()
    return {"deleted": True}
@router.post("/questions/{question_id}/verify")
def verify_question(question_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Not found")
    question.verified = True
    db.commit()
    return {"verified": True}


@router.post("/templates", response_model=TemplateOut)
def create_template(payload: TemplateIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    t = PaperTemplate(**payload.model_dump(), created_by=user.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("/templates", response_model=list[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return db.query(PaperTemplate).all()




@router.get("/templates/{template_id}", response_model=TemplateOut)
def get_template(template_id: int, db: Session = Depends(get_db)):
    t = db.query(PaperTemplate).filter(PaperTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    return t


@router.put("/templates/{template_id}", response_model=TemplateOut)
def update_template(template_id: int, payload: TemplateIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    t = db.query(PaperTemplate).filter(PaperTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump().items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))):
    t = db.query(PaperTemplate).filter(PaperTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(t)
    db.commit()
    return {"deleted": True}
@router.post("/papers/generate")
def generate(template_id: int, avoid_repeat_days: int = 0, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT))):
    paper = generate_paper(db, template_id=template_id, created_by=user.id, avoid_repeat_days=avoid_repeat_days)
    q_ids = [pq.question_id for pq in db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper.id).order_by(PaperQuestion.position)]
    return {"paper_id": paper.id, "question_ids": q_ids}


@router.get("/papers/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(PaperQuestion, Question).join(Question, Question.id == PaperQuestion.question_id).filter(PaperQuestion.paper_id == paper_id).all()
    return [{"position": p.position, "question_id": q.id, "text": q.text, "marks": q.marks} for p, q in paper]


@router.get("/papers/{paper_id}/download")
def download_paper(paper_id: int, db: Session = Depends(get_db)):
    path = create_paper_pdf(db, paper_id, answer_key=False)
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)


@router.get("/papers/{paper_id}/answerkey")
def download_answer(paper_id: int, db: Session = Depends(get_db)):
    path = create_paper_pdf(db, paper_id, answer_key=True)
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)


@router.post("/tests/start")
def start_test(payload: TestStartIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.STUDENT))):
    test = Test(student_id=user.id, paper_id=payload.paper_id)
    db.add(test)
    db.commit()
    db.refresh(test)
    return {"test_id": test.id, "started_at": test.started_at}


@router.post("/tests/{test_id}/answer")
def save_answer(test_id: int, payload: TestAnswerIn, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.STUDENT))):
    test = db.query(Test).filter(Test.id == test_id, Test.student_id == user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    ans = db.query(TestAnswer).filter(TestAnswer.test_id == test_id, TestAnswer.question_id == payload.question_id).first()
    if not ans:
        ans = TestAnswer(test_id=test_id, question_id=payload.question_id)
        db.add(ans)
    ans.selected_key = payload.selected_key
    db.commit()
    return {"saved": True}


@router.post("/tests/{test_id}/submit", response_model=TestSubmitOut)
def submit_test(test_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.STUDENT))):
    test = db.query(Test).filter(Test.id == test_id, Test.student_id == user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    answers = db.query(TestAnswer, Question).join(Question, Question.id == TestAnswer.question_id).filter(TestAnswer.test_id == test_id).all()
    score = 0
    for answer, q in answers:
        correct = answer.selected_key == q.correct_key
        answer.is_correct = correct
        answer.marks_awarded = q.marks if correct and q.type == QuestionType.MCQ else 0
        score += answer.marks_awarded
        if q.chapter_id:
            progress = db.query(StudentProgress).filter(StudentProgress.student_id == user.id, StudentProgress.chapter_id == q.chapter_id).first()
            if not progress:
                progress = StudentProgress(student_id=user.id, chapter_id=q.chapter_id)
                db.add(progress)
            progress.questions_attempted += 1
            progress.correct_answers += 1 if correct else 0
    test.score = score
    test.status = "SUBMITTED"
    test.submitted_at = datetime.now(timezone.utc)
    db.commit()
    return TestSubmitOut(test_id=test.id, score=score)


@router.get("/students/{student_id}/analytics")
def analytics(student_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return student_analytics(db, student_id)
