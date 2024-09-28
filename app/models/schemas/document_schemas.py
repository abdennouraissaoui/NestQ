from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    file_path: str


class DocumentResponse(BaseModel):
    id: int
    filename: str
    created_at: int
    user_id: int

    class Config:
        from_attributes = True
