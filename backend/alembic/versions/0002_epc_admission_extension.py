"""epc admission extension

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-21
"""

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


userrole_new = sa.Enum("ADMIN", "TEACHER", "STUDENT", "COLLEGE", "ASSOCIATE", name="userrole")
appstatus = sa.Enum("PENDING", "APPROVED", "REJECTED", "HOLD", name="applicationstatus")


def upgrade() -> None:
    bind = op.get_bind()
    userrole_new.create(bind, checkfirst=True)
    appstatus.create(bind, checkfirst=True)

    op.add_column("institutions", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column("institutions", sa.Column("institution_type", sa.String(length=80), nullable=True))

    op.add_column("users", sa.Column("phone", sa.String(length=30), nullable=True))
    op.add_column("users", sa.Column("profile_data", sa.JSON(), nullable=True))

    op.create_table(
        "college_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("courses", sa.JSON(), nullable=True),
        sa.Column("fee_structure", sa.JSON(), nullable=True),
        sa.Column("prospectus_url", sa.String(length=500), nullable=True),
        sa.Column("rankings", sa.JSON(), nullable=True),
    )
    op.create_table(
        "admission_applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("course", sa.String(length=255), nullable=False),
        sa.Column("status", appstatus, nullable=False, server_default="PENDING"),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("referred_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "student_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("doc_type", sa.String(length=120), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("ocr_text", sa.Text(), nullable=True),
    )
    op.create_table(
        "verification_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_table(
        "associate_leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("associate_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="NEW"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "associate_commissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("associate_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("admission_applications.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payout_status", sa.String(length=30), nullable=False, server_default="PENDING"),
    )
    op.create_table(
        "ranking_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("ranking_body", sa.String(length=20), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
    )
    op.create_table(
        "past_papers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("processed", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("extracted_blueprint", sa.JSON(), nullable=True),
    )
    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=True),
        sa.Column("insight_type", sa.String(length=60), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("approved", sa.Boolean(), server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_table("ai_insights")
    op.drop_table("past_papers")
    op.drop_table("ranking_snapshots")
    op.drop_table("associate_commissions")
    op.drop_table("associate_leads")
    op.drop_table("verification_tasks")
    op.drop_table("student_documents")
    op.drop_table("admission_applications")
    op.drop_table("college_profiles")
    op.drop_column("users", "profile_data")
    op.drop_column("users", "phone")
    op.drop_column("institutions", "institution_type")
    op.drop_column("institutions", "city")
    appstatus.drop(op.get_bind(), checkfirst=True)
