from datetime import timedelta
import token
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from apex_py.db.db import SessionDep
from apex_py.models.user import User, UserPublic, UserUpdate
from apex_py.utils.jwt import jwt_decode, jwt_encode


user_router = APIRouter(prefix="/api/users")


# 创建用户 - 注册用户
@user_router.post("/add", response_model=UserPublic)
def create_user(user: User, session: SessionDep):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


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
    user_db.sqlmodel_update(user_data)
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


@user_router.post("/login")
async def login(user: User, session: SessionDep):
    find_user = session.exec(select(User).where(user.name == User.name)).first()

    # DEBUG
    print(find_user)

    if not find_user.passwd == user.passwd:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    token = jwt_encode({"username": user.name}, timedelta(minutes=30))
    return {"access_token": token}


@user_router.post("/login/{token}")
async def token_login(token: str, session: SessionDep):
    is_valid, decode_data = jwt_decode(token)

    find_user = session.exec(
        select(User).where(decode_data["username"] == User.name)
    ).first()

    # DEBUG
    print(decode_data)
    print(find_user)

    if not find_user and not is_valid:
        raise HTTPException(status_code=400, detail="token错误或失效，请重新登录")

    return {"msg": "token登录成功，已验证身份有效"}
