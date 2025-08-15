from fastapi import Request
from loguru import logger


def request_loger_M(request: Request):
    logger.debug(f"[{request.method.upper()}] {request.url}")
    return request
