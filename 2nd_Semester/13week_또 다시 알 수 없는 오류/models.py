from sqlalchemy import Column, Integer, String, DateTime
import datetime
from database import Base

class Question(Base):
    # 테이블 명
    __tablename__ = 'question'
    
    # ID : 질문 데이터 고유번호(Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # Subject : 질문 제목
    subject = Column(String, nullable=False)
    
    # Content : 질문 내용
    content = Column(String, nullable=False)
    
    # create_data : 질문 작성일시
    create_date = Column(DateTime, nullable=False, default=datetime.datetime.now)