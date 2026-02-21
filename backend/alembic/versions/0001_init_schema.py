"""init schema

Revision ID: 0001
Revises:
Create Date: 2026-02-21
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("institutions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(length=255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id")), sa.Column("email", sa.String(length=255), nullable=False, unique=True), sa.Column("full_name", sa.String(length=255), nullable=False), sa.Column("password_hash", sa.String(length=255), nullable=False), sa.Column("role", sa.Enum("ADMIN", "TEACHER", "STUDENT", name="userrole"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("subjects", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(length=255), nullable=False), sa.Column("grade", sa.Integer(), nullable=False))
    op.create_table("chapters", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id"), nullable=False), sa.Column("name", sa.String(length=255), nullable=False))
    op.create_table("question_sources", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("file_path", sa.String(length=500), nullable=False), sa.Column("extraction_status", sa.String(length=50), nullable=False), sa.Column("extracted_text", sa.Text()), sa.Column("scanned", sa.Boolean(), server_default=sa.text("false")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("questions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("source_id", sa.Integer(), sa.ForeignKey("question_sources.id")), sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id"), nullable=False), sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("chapters.id")), sa.Column("grade", sa.Integer(), nullable=False), sa.Column("year", sa.Integer()), sa.Column("type", sa.Enum("MCQ", "SHORT", "LONG", "NUMERICAL", name="questiontype"), nullable=False), sa.Column("text", sa.Text(), nullable=False), sa.Column("marks", sa.Integer(), nullable=False), sa.Column("difficulty", sa.Enum("EASY", "MEDIUM", "HARD", name="difficulty"), nullable=False), sa.Column("correct_key", sa.String(length=255)), sa.Column("tags", sa.JSON()), sa.Column("verified", sa.Boolean(), server_default=sa.text("false")), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("options", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False), sa.Column("key", sa.String(length=5), nullable=False), sa.Column("text", sa.Text(), nullable=False), sa.Column("is_correct", sa.Boolean(), server_default=sa.text("false")))
    op.create_table("paper_templates", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(length=255), nullable=False), sa.Column("grade", sa.Integer(), nullable=False), sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id"), nullable=False), sa.Column("blueprint", sa.JSON(), nullable=False), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False))
    op.create_table("generated_papers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("template_id", sa.Integer(), sa.ForeignKey("paper_templates.id"), nullable=False), sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("total_marks", sa.Integer(), nullable=False), sa.Column("duration_minutes", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.create_table("paper_questions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("paper_id", sa.Integer(), sa.ForeignKey("generated_papers.id"), nullable=False), sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False), sa.Column("section_name", sa.String(length=255), nullable=False), sa.Column("position", sa.Integer(), nullable=False))
    op.create_table("tests", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("paper_id", sa.Integer(), sa.ForeignKey("generated_papers.id"), nullable=False), sa.Column("status", sa.String(length=30), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("score", sa.Integer(), server_default="0"))
    op.create_table("test_answers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("test_id", sa.Integer(), sa.ForeignKey("tests.id"), nullable=False), sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False), sa.Column("selected_key", sa.String(length=20)), sa.Column("is_correct", sa.Boolean()), sa.Column("marks_awarded", sa.Integer(), server_default="0"))
    op.create_table("student_progress", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("chapters.id"), nullable=False), sa.Column("questions_attempted", sa.Integer(), server_default="0"), sa.Column("correct_answers", sa.Integer(), server_default="0"), sa.Column("total_time_seconds", sa.Integer(), server_default="0"))


def downgrade() -> None:
    for table in ["student_progress", "test_answers", "tests", "paper_questions", "generated_papers", "paper_templates", "options", "questions", "question_sources", "chapters", "subjects", "users", "institutions"]:
        op.drop_table(table)
