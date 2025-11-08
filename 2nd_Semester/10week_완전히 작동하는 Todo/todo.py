import os
import csv
from typing import List, Dict, Any
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# model.py에서 TodoItem 모델을 가져옵니다.
from model import TodoItem

# --- 상수 정의 (제약사항: 소문자 및 언더스코어) ---
CSV_FILE = 'todos.csv'
CSV_HEADERS = ['id', 'item']

# --- 전역 변수 (수행과제: todo_list) ---
todo_list: List[Dict[str, Any]] = []

# --- CSV 헬퍼 함수 (기존과 동일) ---

def load_todos():
    '''CSV 파일에서 todo 리스트를 불러와 전역 todo_list에 저장합니다.'''
    global todo_list
    todo_list.clear() 
    
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
        return

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # id는 정수(int)로 변환해서 사용해야 비교가 편리합니다.
                row['id'] = int(row['id'])
                todo_list.append(row)
            except ValueError:
                print(f'Warning: Skipping invalid row in CSV: {row}')

def save_todos():
    '''현재 todo_list를 CSV 파일에 덮어씁니다.'''
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(todo_list)

# --- (2) 추가된 부분 ---
# id로 todo 항목을 찾는 헬퍼 함수
def find_todo_by_id(todo_id: int) -> Dict[str, Any] | None:
    '''todo_list에서 id가 일치하는 항목을 찾아 반환합니다.'''
    for todo in todo_list:
        if todo.get('id') == todo_id:
            return todo
    return None

# --- FastAPI 앱 및 라우터 설정 (기존과 동일) ---

app = FastAPI()
router = APIRouter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 서비스에서는 특정 도메인만 지정해야 합니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드(GET, POST, PUT, DELETE 등) 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# --- API 엔드포인트 구현 (기존 + 신규) ---

@router.post('/add_todo')
async def add_todo(todo: Dict[str, Any]):
    '''새로운 todo 항목을 리스트와 CSV에 추가합니다.'''
    if not todo:
        raise HTTPException(status_code=400, detail='경고: 입력값이 비어있습니다.')

    # id 중복 체크 (id가 정수로 들어온다고 가정)
    if find_todo_by_id(int(todo.get('id', 0))):
         raise HTTPException(status_code=400, detail=f"경고: ID {todo.get('id')}가 이미 존재합니다.")

    todo_list.append(todo)
    save_todos()
    
    return {'message': 'Todo added successfully', 'added_todo': todo}

@router.get('/retrieve_todo')
async def retrieve_todo() -> Dict[str, List[Dict[str, Any]]]:
    '''전체 todo_list를 가져옵니다.'''
    return {'todos': todo_list}

@router.get('/get_single_todo/{todo_id}')
async def get_single_todo(todo_id: int):
    '''
    경로 매개변수로 받은 id에 해당하는 todo 항목 1개를 반환합니다.
    '''
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        # 항목이 없으면 404 Not Found 오류를 반환합니다.
        raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')
    
    return todo

@router.put('/update_todo/{todo_id}')
async def update_todo(todo_id: int, todo_item: TodoItem):
    '''
    경로 매개변수로 받은 id의 항목을,
    본문(body)으로 받은 todo_item의 'item' 내용으로 수정합니다.
    '''
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')
    
    # 찾은 항목의 'item' 내용을 수정합니다.
    todo['item'] = todo_item.item
    
    # CSV 파일에 변경 사항을 저장합니다.
    save_todos()
    
    return {'message': 'Todo updated successfully', 'updated_todo': todo}

@router.delete('/delete_single_todo/{todo_id}')
async def delete_single_todo(todo_id: int):
    '''
    경로 매개변수로 받은 id에 해당하는 todo 항목을 삭제합니다.
    '''
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail=f'Todo with id {todo_id} not found')
    
    # 리스트에서 항목을 제거합니다.
    todo_list.remove(todo)
    
    # CSV 파일에 변경 사항을 저장합니다.
    save_todos()
    
    return {'message': 'Todo deleted successfully', 'deleted_todo': todo}

# --- 앱 시작 및 라우터 포함 (기존과 동일) ---

@app.on_event('startup')
def on_startup():
    '''애플리케이션이 시작될 때 CSV 파일에서 데이터를 로드합니다.'''
    load_todos()

app.include_router(router)