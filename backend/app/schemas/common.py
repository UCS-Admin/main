from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.models.entities import Difficulty, QuestionType, UserRole


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole
    institution_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OptionIn(BaseModel):
    key: str
    text: str
    is_correct: bool = False


class OptionOut(OptionIn):
    id: int

    class Config:
        from_attributes = True


class QuestionIn(BaseModel):
    source_id: Optional[int] = None
    subject_id: int
    chapter_id: Optional[int] = None
    grade: int
    year: Optional[int] = None
    type: QuestionType
    text: str
    marks: int
    difficulty: Difficulty
    correct_key: Optional[str] = None
    tags: Optional[dict] = None
    options: List[OptionIn] = []


class QuestionOut(BaseModel):
    id: int
    source_id: Optional[int]
    subject_id: int
    chapter_id: Optional[int]
    grade: int
    year: Optional[int]
    type: QuestionType
    text: str
    marks: int
    difficulty: Difficulty
    correct_key: Optional[str]
    tags: Optional[dict]
    verified: bool
    options: List[OptionOut] = []

    class Config:
        from_attributes = True


class TemplateIn(BaseModel):
    title: str
    grade: int
    subject_id: int
    blueprint: dict


class TemplateOut(TemplateIn):
    id: int

    class Config:
        from_attributes = True


class TestStartIn(BaseModel):
    paper_id: int


class TestAnswerIn(BaseModel):
    question_id: int
    selected_key: str


class TestSubmitOut(BaseModel):
    test_id: int
    score: int
