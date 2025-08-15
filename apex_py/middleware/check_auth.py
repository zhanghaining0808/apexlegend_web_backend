from fastapi import Request

from apex_py.models.apex_http_exception import ApexHTTPException
from apex_py.utils.jwt import jwt_decode


def check_auth_M(request: Request):
    # X-Auth-Token随便取的, 可以任意修改
    token = request.headers.get("X-Auth-Token", None)
    if not token:
        raise ApexHTTPException(status_code=400, detail="授权token不存在, 拒绝访问!!!")

    # 只判断是否没过期合法, 解析出来的值暂时用不上, 用_表示忽略
    is_valid, _ = jwt_decode(token)

    if not is_valid:
        raise ApexHTTPException(status_code=400, detail="授权token合法, 拒绝访问!!!")

    return request
