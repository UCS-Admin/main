from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.models.entities import GeneratedPaper, PaperQuestion, Question


def _paper_questions(db: Session, paper_id: int):
    return (
        db.query(PaperQuestion, Question)
        .join(Question, Question.id == PaperQuestion.question_id)
        .filter(PaperQuestion.paper_id == paper_id)
        .order_by(PaperQuestion.position)
        .all()
    )


def create_paper_pdf(db: Session, paper_id: int, answer_key: bool = False) -> str:
    paper = db.query(GeneratedPaper).filter(GeneratedPaper.id == paper_id).first()
    if not paper:
        raise ValueError("Paper not found")
    out_dir = Path("generated")
    out_dir.mkdir(exist_ok=True)
    suffix = "answerkey" if answer_key else "paper"
    path = out_dir / f"paper_{paper_id}_{suffix}.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    y = 800
    c.drawString(50, y, f"Paper #{paper_id} | Total Marks: {paper.total_marks} | Duration: {paper.duration_minutes} min")
    y -= 30
    for idx, (_, q) in enumerate(_paper_questions(db, paper_id), start=1):
        line = f"Q{idx}. {q.text} ({q.marks})"
        if answer_key and q.correct_key:
            line += f" | Ans: {q.correct_key}"
        c.drawString(50, y, line[:140])
        y -= 20
        if y < 60:
            c.showPage()
            y = 800
    c.save()
    return str(path)
