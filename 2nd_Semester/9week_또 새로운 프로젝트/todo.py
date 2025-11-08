import os
import csv
from typing import List, Dict, Any
from fastapi import FastAPI, APIRouter, HTTPException

# --- 상수 정의 (제약사항: 소문자 및 언더스코어) ---
CSV_FILE = 'todos.csv'
CSV_HEADERS = ['id', 'item']

# --- 전역 변수 (수행과제: todo_list) ---
# 앱 실행 시 load_todos() 함수를 통해 CSV에서 데이터를 읽어와 채워집니다.
todo_list: List[Dict[str, Any]] = []

# --- CSV 헬퍼 함수 (제약사항: CSV 사용) ---

def load_todos():
    '''CSV 파일에서 todo 리스트를 불러와 전역 todo_list에 저장합니다.'''
    global todo_list
    todo_list.clear() # 기존 리스트 비우기
    
    if not os.path.exists(CSV_FILE):
        # CSV 파일이 없으면 헤더만 있는 빈 파일 생성
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
        return

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        # DictReader를 사용해 CSV를 딕셔너리 리스트로 읽어옵니다.
        reader = csv.DictReader(f)
        for row in reader:
            # CSV에서 읽은 값은 문자열이므로, id는 int로 변환 (선택 사항)
            try:
                row['id'] = int(row['id'])
                todo_list.append(row)
            except ValueError:
                print(f'Warning: Skipping invalid row in CSV: {row}')

def save_todos():
    '''현재 todo_list를 CSV 파일에 덮어씁니다.'''
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        # DictWriter를 사용해 딕셔너리 리스트를 CSV로 씁니다.
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(todo_list)

# --- FastAPI 앱 및 라우터 설정 ---

app = FastAPI()
router = APIRouter()

# --- API 엔드포인트 구현 (수행과제) ---

@router.post('/add_todo')
async def add_todo(todo: Dict[str, Any]):
    '''
    새로운 todo 항목을 리스트와 CSV에 추가합니다.
    입력값은 Dict 타입입니다.
    '''
    # 보너스 과제: 입력된 Dict가 비어있는지 확인
    if not todo:
        # 비어있다면 400 Bad Request와 함께 경고 메시지 반환
        raise HTTPException(status_code=400, detail='경고: 입력값이 비어있습니다.')

    # todo_list에 항목 추가
    todo_list.append(todo)
    
    # 제약사항: CSV 파일에 저장
    save_todos()
    
    # 수행과제: 출력은 Dict 타입
    return {'message': 'Todo added successfully', 'added_todo': todo}

@router.get('/retrieve_todo')
async def retrieve_todo() -> Dict[str, List[Dict[str, Any]]]:
    '''
    전체 todo_list를 가져옵니다.
    출력값은 Dict 타입입니다.
    '''
    # 수행과제: todo_list를 가져온다.
    # 수행과제: 출력은 Dict 타입 (list를 dict로 감싸서 반환)
    return {'todos': todo_list}

# --- 앱 시작 시 CSV 로드 ---

@app.on_event('startup')
def on_startup():
    '''애플리케이션이 시작될 때 CSV 파일에서 데이터를 로드합니다.'''
    load_todos()

# 라우터를 메인 앱에 포함
app.include_router(router)

# uvicorn 실행을 위한 메인 (선택 사항이지만 uvicorn todo:app --reload와 동일)
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('todo:app', host='127.0.0.1', port=8000, reload=True)