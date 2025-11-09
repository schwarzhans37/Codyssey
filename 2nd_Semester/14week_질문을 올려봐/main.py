from fastapi import FastAPI
from domain.question import question_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# FastAPI 앱 생성
app = FastAPI()

# Include_router를 통해 question_router.py의 API들을 앱에 등록
app.include_router(question_router.router)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')