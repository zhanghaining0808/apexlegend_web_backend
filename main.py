from fastapi import FastAPI
import uvicorn

from apex_py.db.db import create_db_and_tables
from apex_py.controls.ctr_hero import hero_router

app = FastAPI()
app.include_router(hero_router)


# 在启动时创建数据库表
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=25357,
    )
