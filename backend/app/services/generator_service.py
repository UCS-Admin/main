from collections import defaultdict
from datetime import datetime, timedelta, timezone
import random

from sqlalchemy.orm import Session

from app.models.entities import GeneratedPaper, PaperQuestion, PaperTemplate, Question, QuestionType


def _pick_with_difficulty(pool, required_count, ratio):
    target = {
        "EASY": round(required_count * ratio.get("easy", 30) / 100),
        "MEDIUM": round(required_count * ratio.get("medium", 50) / 100),
    }
    target["HARD"] = max(0, required_count - target["EASY"] - target["MEDIUM"])
    picked = []
    used = set()
    by_diff = defaultdict(list)
    for q in pool:
        by_diff[q.difficulty.value].append(q)

    for diff in ["EASY", "MEDIUM", "HARD"]:
        candidates = by_diff[diff]
        random.shuffle(candidates)
        for q in candidates[: target[diff]]:
            if q.id not in used:
                picked.append(q)
                used.add(q.id)

    if len(picked) < required_count:
        remaining = [q for q in pool if q.id not in used]
        random.shuffle(remaining)
        picked.extend(remaining[: required_count - len(picked)])

    return picked[:required_count]


def generate_paper(db: Session, template_id: int, created_by: int, avoid_repeat_days: int = 0):
    template = db.query(PaperTemplate).filter(PaperTemplate.id == template_id).first()
    if not template:
        raise ValueError("Template not found")

    blueprint = template.blueprint
    sections = blueprint.get("sections", [])
    ratio = blueprint.get("difficultyRatio", {"easy": 30, "medium": 50, "hard": 20})

    cutoff = datetime.now(timezone.utc) - timedelta(days=avoid_repeat_days)
    recent_question_ids = {
        pq.question_id
        for pq in db.query(PaperQuestion)
        .join(GeneratedPaper, GeneratedPaper.id == PaperQuestion.paper_id)
        .filter(GeneratedPaper.created_at >= cutoff)
        .all()
    } if avoid_repeat_days else set()

    paper = GeneratedPaper(
        template_id=template.id,
        created_by=created_by,
        total_marks=blueprint.get("totalMarks", 0),
        duration_minutes=blueprint.get("duration", 60),
    )
    db.add(paper)
    db.flush()

    order = 1
    globally_used = set()
    for section in sections:
        qtype = QuestionType(section["type"])
        count = section["count"]
        marks_each = section["marksEach"]
        base_query = db.query(Question).filter(
            Question.grade == template.grade,
            Question.subject_id == template.subject_id,
            Question.verified.is_(True),
            Question.type == qtype,
            Question.marks == marks_each,
        )
        chapter_ids = section.get("chapterIds") or blueprint.get("chapterWeightage", {}).keys()
        if chapter_ids:
            base_query = base_query.filter(Question.chapter_id.in_(list(map(int, chapter_ids))))

        pool = [q for q in base_query.all() if q.id not in recent_question_ids and q.id not in globally_used]
        if len(pool) < count:
            pool = [q for q in base_query.all() if q.id not in globally_used]
        selected = _pick_with_difficulty(pool, count, ratio)
        for question in selected:
            db.add(PaperQuestion(paper_id=paper.id, question_id=question.id, section_name=section["name"], position=order))
            globally_used.add(question.id)
            order += 1

    db.commit()
    return paper
