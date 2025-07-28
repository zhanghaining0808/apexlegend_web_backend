from fastapi import FastAPI
import uvicorn

from apex_py.db.db import create_db_and_tables
from apex_py.controls.ctr_hero import hero_router
from apex_py.controls.ctr_user import user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# 设置允许的源列表
origins = [
    "http://localhost:5173",  # Vue 开发服务器
    "http://127.0.0.1:5173",  # 有时浏览器会使用这个地址
    # 可以添加其他需要的前端地址
]


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 或使用 ["*"] 允许所有源（不推荐生产环境）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

app.include_router(hero_router)

app.include_router(user_router)


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
