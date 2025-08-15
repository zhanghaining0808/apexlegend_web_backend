from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlmodel import select

from apex_py.db.db import SessionDep
from apex_py.middleware.request_loger import request_loger_M
from apex_py.models.apex_http_exception import ApexHTTPException
from apex_py.models.hero import Hero, HeroUpdateReq
from apex_py.middleware.check_auth import check_auth_M
from apex_py.models.response import ApexResponse

# 最好使用/api 表示前缀
# prefix表示前缀
# 因为我这里希望hero相关的全部api都需要授权后使用,我们可以直接让这个路由使用我们的check_auth中间件
hero_router = APIRouter(
    prefix="/api/heroes",
    dependencies=[Depends(request_loger_M), Depends(check_auth_M)],
)


# 创建
@hero_router.post("/add", response_model=ApexResponse)
def create_hero(hero: Hero, session: SessionDep):
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return ApexResponse(data=hero.model_dump(), msg="创建Apex英雄成功")


# read_heros 读取全部英雄
# 利用limit和offset来对结果进行分页处理
# 使用 response_model=list[HeroPublic] 确保正确地验证和序列化数据
@hero_router.get("/query", response_model=ApexResponse)
def read_all_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return ApexResponse(data=list(heroes), msg="获取全部英雄成功")


# 用Public读取单个英雄id
# TODO 待测试
@hero_router.get("/query/{hero_id}", response_model=ApexResponse)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise ApexHTTPException(status_code=404, detail="英雄未找到！")
    return ApexResponse(data=list(hero), msg="读取单个英雄成功")


# # 根据英雄名称来获取英雄信息


# 更新单个英雄
# 我们可以更新单个 hero 。为此，我们会使用 HTTP 的 PATCH 操作
@hero_router.post("/update/{hero_id}", response_model=ApexResponse)
def update_hero(hero_id: int, hero_update_req: HeroUpdateReq, session: SessionDep):
    find_hero = session.get(Hero, hero_id)
    need_update_hero = hero_update_req.update_hero.model_dump()

    if not need_update_hero:
        raise ApexHTTPException(status_code=404, detail="英雄新数据未找到！")
    if not find_hero:
        raise ApexHTTPException(status_code=404, detail="英雄旧数据未找到！")

    old_hero = find_hero.model_dump()
    new_hero = old_hero

    for need_update_key in hero_update_req.update_key:
        print(need_update_key)
        if need_update_key in old_hero.keys():
            new_hero[need_update_key] = need_update_hero[need_update_key]

    find_hero.sqlmodel_update(new_hero)
    session.commit()
    session.refresh(find_hero)
    return ApexResponse(data=find_hero.model_dump(), msg="更新单个英雄成功")


# 删除单个英雄id
@hero_router.post("/delete/{hero_id}", response_model=ApexResponse)
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise ApexHTTPException(status_code=404, detail="该英雄未找到!")
    session.delete(hero)
    session.commit()
    return ApexResponse(data=hero.model_dump(), msg="英雄已删除!")
