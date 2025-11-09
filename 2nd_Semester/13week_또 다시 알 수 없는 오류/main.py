from fastapi import FastAPI
from domain.question import question_router

# FastAPI 앱 생성
app = FastAPI()

# Include_router를 통해 question_router.py의 API들을 앱에 등록
app.include_router(question_router.router)