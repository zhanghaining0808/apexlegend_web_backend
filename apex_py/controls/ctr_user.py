from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from apex_py.db.db import SessionDep
from apex_py.middleware.check_auth import check_auth_M
from apex_py.middleware.request_loger import request_loger_M
from apex_py.models.apex_http_exception import ApexHTTPException
from apex_py.models.response import ApexResponse
from apex_py.models.user import User, UserUpdateReq
from apex_py.utils.jwt import jwt_decode, jwt_encode
from apex_py.utils.security import get_passwd_hash, verify_passwd


user_router = APIRouter(prefix="/api/users", dependencies=[Depends(request_loger_M)])


# 创建用户 - 注册用户
# @user_router.post("/add", response_model=UserPublic) x错误的，和{"user": user, "access_token": token}不匹配，如果只是return user，这样写就没问题
@user_router.post("/add", response_model=ApexResponse)
def create_user(user: User, session: SessionDep):
    find_user = session.exec(select(User).where(user.name == User.name)).first()
    if find_user:
        raise ApexHTTPException(
            status_code=400, detail="相同用户名称已存在, 请更换用户名!"
        )
    # 对密码进行哈希后存储(不再存储明文)
    user.passwd = get_passwd_hash(user.passwd)

    session.add(user)
    session.commit()
    session.refresh(user)
    token = jwt_encode({"username": user.name}, timedelta(days=3))

    return ApexResponse(data={"user": user, "access_token": token}, msg="创建用户成功")


# 读取全部用户
@user_router.get(
    "/query", response_model=ApexResponse, dependencies=[Depends(check_auth_M)]
)
def read_all_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return ApexResponse(data=list(users), msg="获取全部用户成功")


# 读取单个用户
@user_router.get("/query/{user_id}", response_model=ApexResponse)
def read_hero(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise ApexHTTPException(status_code=404, detail="用户未找到！")
    return ApexResponse(data=list(user), msg="获取单个用户成功")


# 更新单个用户
@user_router.post("/update/{user_id}", response_model=ApexResponse)
def update_user(user_id: int, user_update_req: UserUpdateReq, session: SessionDep):
    find_user = session.get(User, user_id)
    need_update_user = user_update_req.update_user.model_dump()
    if not need_update_user:
        raise ApexHTTPException(status_code=404, detail="用户新数据未找到！")
    if not find_user:
        raise ApexHTTPException(status_code=404, detail="用户旧数据未找到！")

    old_user = find_user.model_dump()
    new_user = old_user
    for need_update_key in user_update_req.update_key:
        print(need_update_key)
        if need_update_key in old_user.keys():
            new_user[need_update_key] = need_update_user[need_update_key]

    find_user.sqlmodel_update(new_user)
    session.commit()
    session.refresh(find_user)
    return ApexResponse(data=find_user.model_dump(), msg="更新单个用户成功")


# 删除单个用户
@user_router.post("/delete/{user_id}", response_model=ApexResponse)
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise ApexHTTPException(status_code=404, detail="该用户未找到!")
    session.delete(user)
    session.commit()
    return ApexResponse(data=user.model_dump(), msg="用户已删除!")


# 登录功能
@user_router.post("/login", response_model=ApexResponse)
async def login(user: User, session: SessionDep):
    find_user = session.exec(select(User).where(User.name == user.name)).first()

    # DEBUG
    print(find_user)

    if not find_user:
        raise ApexHTTPException(status_code=400, detail="用户或密码错误")

    if not verify_passwd(user.passwd, find_user.passwd):
        raise ApexHTTPException(status_code=400, detail="用户或密码错误")

    token = jwt_encode({"username": user.name}, timedelta(days=3))

    return ApexResponse(
        data={
            "user": {"name": find_user.name, "phone": find_user.phone},
            "access_token": token,
        },
        msg="用户登录成功",
    )


@user_router.post("/login/{token}", response_model=ApexResponse)
async def token_login(token: str, session: SessionDep):
    is_valid, decode_data = jwt_decode(token)

    if not decode_data:
        raise ApexHTTPException(
            400, detail="token 不存在数据，或token失效，请重新登录!"
        )

    find_user = session.exec(
        select(User).where(decode_data["username"] == User.name)
    ).first()

    # DEBUG
    print(decode_data)
    print(find_user)

    if not find_user:
        raise ApexHTTPException(status_code=400, detail="token错误或失效，请重新登录")
    if not is_valid:
        raise ApexHTTPException(status_code=400, detail="token错误或失效，请重新登录")

    return ApexResponse(
        data={"user": {"name": find_user.name, "phone": find_user.phone}},
        msg="token登录成功，已验证身份有效",
    )  # type: ignore
