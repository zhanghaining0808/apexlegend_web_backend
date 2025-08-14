from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from apex_py.utils.config import load_config

config = load_config()

postgres_url = (
    f"postgresql://{config.DB_USER}:{config.DB_PASSWD}@localhost:5432/{config.DB_NAME}"
)
engine = create_engine(postgres_url)


# 添加一个函数为所有表模型创建表。
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 创建会话(Session)依赖项
def get_session():
    with Session(engine) as session:
        yield session


# 这里创建一个annotated的依赖项来简化其他会用到的此类代码
SessionDep = Annotated[Session, Depends(get_session)]
