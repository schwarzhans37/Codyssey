from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from contextlib import AbstractContextManager

# get_db와 models.py의 Question 모델을 가져오기
from database import get_db
from models import Question as QuestionModel
from .question_schema import QuestionSchema

# "/api/question"을 기본 주소(Prefix)로 사용하는 라우터 생성
router = APIRouter(
    prefix="/api/question",
)

@router.get("/", response_model=List[QuestionSchema])
def question_list(
    db_context: AbstractContextManager[Session] = Depends(get_db)
):
    """
    질문 목록 조회 API
    """
    
    with db_context as db:
        _question_list = db.query(QuestionModel).all()
        return _question_list