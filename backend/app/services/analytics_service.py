from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Chapter, Question, StudentProgress, Test


def student_analytics(db: Session, student_id: int):
    tests = db.query(Test).filter(Test.student_id == student_id).all()
    attempted = len(tests)
    avg_score = sum(t.score for t in tests) / attempted if attempted else 0
    chapter_stats = (
        db.query(Chapter.name, func.sum(StudentProgress.questions_attempted), func.sum(StudentProgress.correct_answers))
        .join(StudentProgress, StudentProgress.chapter_id == Chapter.id)
        .filter(StudentProgress.student_id == student_id)
        .group_by(Chapter.name)
        .all()
    )
    weak = [c[0] for c in chapter_stats if c[1] and (c[2] / c[1]) < 0.5]
    return {"tests_attempted": attempted, "avg_score": avg_score, "weak_chapters": weak}
