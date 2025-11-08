from pydantic import BaseModel

class TodoItem(BaseModel):
    '''
    수정(PUT) 요청 시 본문(body)으로 받을 데이터 모델입니다.
    id는 경로(path)로 받기 때문에, 실제 내용은 'item' 필드만 받습니다.
    '''
    item: str