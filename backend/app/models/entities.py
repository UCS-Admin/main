import enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    COLLEGE = "COLLEGE"
    ASSOCIATE = "ASSOCIATE"


class Difficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    SHORT = "SHORT"
    LONG = "LONG"
    NUMERICAL = "NUMERICAL"


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    HOLD = "HOLD"


class Institution(Base):
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    city = Column(String(120), nullable=True)
    institution_type = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    phone = Column(String(30), nullable=True)
    profile_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    grade = Column(Integer, nullable=False)


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(255), nullable=False)


class QuestionSource(Base):
    __tablename__ = "question_sources"
    id = Column(Integer, primary_key=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    extraction_status = Column(String(50), nullable=False, default="UPLOADED")
    extracted_text = Column(Text, nullable=True)
    scanned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("question_sources.id"), nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    grade = Column(Integer, nullable=False)
    year = Column(Integer, nullable=True)
    type = Column(Enum(QuestionType), nullable=False)
    text = Column(Text, nullable=False)
    marks = Column(Integer, nullable=False)
    difficulty = Column(Enum(Difficulty), nullable=False)
    correct_key = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    verified = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")


class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    key = Column(String(5), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    question = relationship("Question", back_populates="options")


class PaperTemplate(Base):
    __tablename__ = "paper_templates"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    grade = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    blueprint = Column(JSON, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)


class GeneratedPaper(Base):
    __tablename__ = "generated_papers"
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("paper_templates.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_marks = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PaperQuestion(Base):
    __tablename__ = "paper_questions"
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("generated_papers.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    section_name = Column(String(255), nullable=False)
    position = Column(Integer, nullable=False)


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("generated_papers.id"), nullable=False)
    status = Column(String(30), default="STARTED")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    score = Column(Integer, default=0)


class TestAnswer(Base):
    __tablename__ = "test_answers"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_key = Column(String(20), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    marks_awarded = Column(Integer, default=0)


class StudentProgress(Base):
    __tablename__ = "student_progress"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    questions_attempted = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_time_seconds = Column(Integer, default=0)


class CollegeProfile(Base):
    __tablename__ = "college_profiles"
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    description = Column(Text, nullable=True)
    courses = Column(JSON, nullable=True)
    fee_structure = Column(JSON, nullable=True)
    prospectus_url = Column(String(500), nullable=True)
    rankings = Column(JSON, nullable=True)


class AdmissionApplication(Base):
    __tablename__ = "admission_applications"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    course = Column(String(255), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    remarks = Column(Text, nullable=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentDocument(Base):
    __tablename__ = "student_documents"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doc_type = Column(String(120), nullable=False)
    file_path = Column(String(500), nullable=False)
    verified = Column(Boolean, default=False)
    ocr_text = Column(Text, nullable=True)


class VerificationTask(Base):
    __tablename__ = "verification_tasks"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    status = Column(String(30), default="PENDING")
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)


class AssociateLead(Base):
    __tablename__ = "associate_leads"
    id = Column(Integer, primary_key=True)
    associate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    status = Column(String(30), default="NEW")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AssociateCommission(Base):
    __tablename__ = "associate_commissions"
    id = Column(Integer, primary_key=True)
    associate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("admission_applications.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payout_status = Column(String(30), default="PENDING")


class RankingSnapshot(Base):
    __tablename__ = "ranking_snapshots"
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    ranking_body = Column(String(20), nullable=False)
    rank = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)


class PastPaper(Base):
    __tablename__ = "past_papers"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade = Column(Integer, nullable=False)
    year = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    processed = Column(Boolean, default=False)
    extracted_blueprint = Column(JSON, nullable=True)


class AIInsight(Base):
    __tablename__ = "ai_insights"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    insight_type = Column(String(60), nullable=False)
    content = Column(Text, nullable=False)
    approved = Column(Boolean, default=False)
