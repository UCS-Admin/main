from pydantic import BaseModel


class ApplicationIn(BaseModel):
    institution_id: int
    course: str


class ApplicationStatusIn(BaseModel):
    status: str
    remarks: str | None = None


class LeadIn(BaseModel):
    student_id: int
    institution_id: int | None = None


class RankingIn(BaseModel):
    institution_id: int
    ranking_body: str
    rank: int
    year: int
