import os
from typing import Dict
from dotenv import load_dotenv
from pydantic import BaseModel


# 建一个config配置类
# 这个类里面的字段表示我们可配置的功能有哪些
class Config(BaseModel):
    HOSTNAME: str
    PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWD: str


def load_config() -> Config:
    load_dotenv(".env")

    envs = os.environ

    return Config(**dict(envs))  # type: ignore
