import sys
import uvicorn

from fastapi import FastAPI
from apex_py.db.db import create_db_and_tables
from apex_py.controls.ctr_hero import hero_router
from apex_py.controls.ctr_user import user_router
from apex_py.controls.ctr_weapon import weapon_router
from fastapi.middleware.cors import CORSMiddleware
from apex_py.utils.config import load_config
from loguru import logger


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
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


if __name__ == "__main__":
    config = load_config()

    # 先移除默认handler（避免重复输出）
    logger.remove()
    # 终端日志输出配置
    logger.add(
        sink=sys.stderr,
        format=config.LOG_CONSOLE_FORMAT,
        level=config.LOG_CONSOLE_LEVEL,
    )
    # 日志文件输出配置
    logger.add(
        config.LOG_FILE_PATH, format=config.LOG_FILE_FORMAT, level=config.LOG_FILE_LEVEL
    )
    logger.debug("我是调试信息")
    logger.info("我是基本输出信息")
    logger.warning("我是一个警告信息")
    logger.error("我是一个错误信息")
    uvicorn.run(
        "main:app",
        host=config.HOSTNAME,
        port=config.PORT,
    )
