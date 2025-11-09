from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# 1. SQLite 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./myapi.db"

# 2. SQAlchemy 'engine'
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # SQLite는 connect_args가 필요
    connect_args={"check_same_thread": False}
)

# 3. 데이터베이스 세션 생성 (autocommit = false가 기본값)
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

# 4. 모델이 상속할 'Base' 클래스 생성
Base = declarative_base()

@contextmanager
def get_db():
    """
    FastAPI의 Depends를 통해 DB 세션을 관리하는 함수
    요청이 시작될 때 세션을 생성하고, 끝나면 닫음.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()