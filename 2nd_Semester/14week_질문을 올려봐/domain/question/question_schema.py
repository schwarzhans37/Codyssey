import datetime
from pydantic import BaseModel, Field

class QuestionSchema(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime.datetime
    
    # [ 13주차 - 보너스 과제 ]
    # orm_mode = True 설정이 없으면, SQLAlchemy 모델 객체를 Pydantic 스키마로 읽지 못하게
    class Config:
        orm_mode = True
        
class QuestionCreate(BaseModel):
    subject: str = Field(min_length=1)
    content: str = Field(min_length=1)