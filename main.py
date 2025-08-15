import uvicorn

from fastapi import FastAPI
from apex_py.db.db import create_db_and_tables
from apex_py.controls.ctr_hero import hero_router
from apex_py.controls.ctr_user import user_router
from apex_py.controls.ctr_weapon import weapon_router
from fastapi.middleware.cors import CORSMiddleware
from apex_py.middleware.request_loger import request_loger_M
from apex_py.utils.config import load_config
from loguru import logger

from apex_py.utils.logger import init_logger


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
    # 设置允许哪些"来源"(域名)可以访问你的API
    # 示例：origins = ["http://localhost:3000", "https://yourfrontend.com"]
    # 使用["*"]表示允许所有网站访问(不安全，仅建议开发用)
    allow_credentials=True,
    # 允许浏览器在跨域请求中发送凭证(如cookies, HTTP认证等)
    allow_methods=["*"],  # 允许所有方法
    # 允许所有HTTP方法(GET, POST, PUT等)
    # 也可以指定具体方法：["GET", "POST"]
    allow_headers=["*"],  # 允许所有头
    # 允许请求中携带所有类型的头信息
)

app.include_router(hero_router)

app.include_router(user_router)

app.include_router(weapon_router)


# 在启动时创建数据库表
# P1、2、3 表示修复优先级
# P1表示严重，P2表示中等，P3表示警告，有时间修复即可
# FIXME [P3] 修复函数弃用问题，采用官网最新的函数API
@app.on_event("startup")
def on_startup():
    logger.info("服务启动成功")
    logger.info("开始初始化数据表...")
    create_db_and_tables()
    logger.info("数据表初始化成功")


if __name__ == "__main__":
    config = load_config()
    init_logger(config=config)
    logger.info(f"{8*'*'} Apexlegend WEB Backend {8*'*'}")
    logger.info("启动服务中...")

    uvicorn.run(
        "main:app",
        host=config.HOSTNAME,
        port=config.PORT,
    )
