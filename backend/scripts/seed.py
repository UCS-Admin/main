from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.entities import (
    Chapter,
    CollegeProfile,
    Difficulty,
    Institution,
    PastPaper,
    Question,
    QuestionType,
    Subject,
    User,
    UserRole,
)


def get_or_create_user(db, email, name, role, institution_id=None):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=name,
            password_hash=get_password_hash("pass123"),
            role=role,
            institution_id=institution_id,
        )
        db.add(user)
        db.flush()
    return user


def run():
    db = SessionLocal()

    college = db.query(Institution).filter(Institution.name == "EPC Institute of Technology").first()
    if not college:
        college = Institution(name="EPC Institute of Technology", city="Mumbai", institution_type="University")
        db.add(college)
        db.flush()

    get_or_create_user(db, "admin@example.com", "Admin", UserRole.ADMIN)
    get_or_create_user(db, "student@example.com", "Student One", UserRole.STUDENT)
    get_or_create_user(db, "associate@example.com", "Associate One", UserRole.ASSOCIATE)
    get_or_create_user(db, "college@example.com", "College Manager", UserRole.COLLEGE, institution_id=college.id)

    profile = db.query(CollegeProfile).filter(CollegeProfile.institution_id == college.id).first()
    if not profile:
        db.add(
            CollegeProfile(
                institution_id=college.id,
                description="Top ranked institute with EPC integrated admissions.",
                courses=["B.Tech CSE", "BBA", "MBA"],
                fee_structure={"B.Tech CSE": 180000, "BBA": 120000},
                rankings={"NIRF": 42, "QS": 520, "NAAC": "A+"},
            )
        )

    subject = db.query(Subject).filter(Subject.name == "Mathematics", Subject.grade == 10).first()
    if not subject:
        subject = Subject(name="Mathematics", grade=10)
        db.add(subject)
        db.flush()

    chapter = db.query(Chapter).filter(Chapter.name == "Algebra", Chapter.subject_id == subject.id).first()
    if not chapter:
        chapter = Chapter(subject_id=subject.id, name="Algebra")
        db.add(chapter)
        db.flush()

    admin = db.query(User).filter(User.email == "admin@example.com").first()

    if not db.query(Question).first():
        for i in range(1, 31):
            db.add(
                Question(
                    subject_id=subject.id,
                    chapter_id=chapter.id,
                    grade=10,
                    type=QuestionType.MCQ if i % 2 else QuestionType.SHORT,
                    text=f"Sample question {i}?",
                    marks=1 if i % 2 else 3,
                    difficulty=[Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD][i % 3],
                    correct_key="A" if i % 2 else None,
                    verified=True,
                    created_by=admin.id,
                    year=2015 + (i % 10),
                )
            )

    if not db.query(PastPaper).first():
        db.add(PastPaper(title="Math Board Paper", subject_id=subject.id, grade=10, year=2024, file_path="uploads/sample.pdf", uploaded_by=admin.id, processed=False))

    db.commit()
    db.close()


if __name__ == "__main__":
    run()
