from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# get_db와 models.py의 Question 모델을 가져오기
from database import get_db
from models import Question

# "/api/question"을 기본 주소(Prefix)로 사용하는 라우터 생성
router = APIRouter(
    prefix="/api/question",
)

# GET으로 /api/question/(prefix + "/") 주소를 API화
# 함수 이름은 question_list
@router.get("/")
def question_list(db: Session = Depends(get_db)):
    """
    질문 목록을 조회하는 API
    ORM을 사용해 Question 테이블의 모든 데이터 불러오기
    """
    _question_list=db.query(Question).all()
    
    return _question_list