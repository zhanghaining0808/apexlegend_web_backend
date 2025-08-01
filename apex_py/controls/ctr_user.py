from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from apex_py.db.db import SessionDep
from apex_py.models.user import User, UserPublic, UserUpdate
from apex_py.utils.jwt import jwt_decode, jwt_encode
from apex_py.utils.security import get_passwd_hash, verify_passwd


user_router = APIRouter(prefix="/api/users")


# 创建用户 - 注册用户
# @user_router.post("/add", response_model=UserPublic) x错误的，和{"user": user, "access_token": token}不匹配，如果只是return user，这样写就没问题
@user_router.post("/add")
def create_user(user: User, session: SessionDep):
    find_user = session.exec(select(User).where(user.name == User.name)).first()
    if find_user:
        raise HTTPException(status_code=400, detail="相同用户名称已存在, 请更换用户名!")
    # 对密码进行哈希后存储(不再存储明文)
    user.passwd = get_passwd_hash(user.passwd)

    session.add(user)
    session.commit()
    session.refresh(user)
    token = jwt_encode({"username": user.name}, timedelta(minutes=30))

    return {"user": user, "access_token": token}


# 读取全部用户
@user_router.get("/query", response_model=list[UserPublic])
def read_all_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


# 读取单个用户
@user_router.get("/query/{user_id}", response_model=UserPublic)
def read_hero(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到！")
    return user


# 更新单个用户
@user_router.patch("/update/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到！")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)  # type: ignore
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


# 删除单个用户
@user_router.post("/delete/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="该用户未找到!")
    session.delete(user)
    session.commit()
    return user


# 登录功能
@user_router.post("/login")
async def login(user: User, session: SessionDep):
    find_user = session.exec(select(User).where(User.name == user.name)).first()

    # DEBUG
    print(find_user)

    if not find_user:
        raise HTTPException(status_code=400, detail="用户或密码错误")

    if not verify_passwd(user.passwd, find_user.passwd):
        raise HTTPException(status_code=400, detail="用户或密码错误")

    token = jwt_encode({"username": user.name}, timedelta(minutes=30))

    return {
        "user": {"name": find_user.name, "phone": find_user.phone},
        "access_token": token,
    }


@user_router.post("/login/{token}")
async def token_login(token: str, session: SessionDep):
    is_valid, decode_data = jwt_decode(token)

    if not decode_data:
        raise HTTPException(400, detail="token 不存在数据，或token失效，请重新登录!")

    find_user = session.exec(
        select(User).where(decode_data["username"] == User.name)
    ).first()

    # DEBUG
    print(decode_data)
    print(find_user)

    if not find_user and not is_valid:
        raise HTTPException(status_code=400, detail="token错误或失效，请重新登录")

    return {"user": {"name": find_user.name, "phone": find_user.phone}, "msg": "token登录成功，已验证身份有效"}  # type: ignore
