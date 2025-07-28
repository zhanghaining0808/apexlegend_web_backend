from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from apex_py.db.db import SessionDep
from apex_py.models.hero import Hero, HeroPublic, HeroUpdate

# 最好使用/api 表示前缀
hero_router = APIRouter(prefix="/api/heroes")
# prefix表示前缀


# 创建
@hero_router.post("/add", response_model=HeroPublic)
def create_hero(hero: Hero, session: SessionDep):
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


# read_heros 读取全部英雄
# 利用limit和offset来对结果进行分页处理
# 使用 response_model=list[HeroPublic] 确保正确地验证和序列化数据
@hero_router.get("/query", response_model=list[HeroPublic])
def read_all_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


# 用Public读取单个英雄id
@hero_router.get("/query/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="英雄未找到！")
    return hero


# # 根据英雄名称来获取英雄信息


# 更新单个英雄
# 我们可以更新单个 hero 。为此，我们会使用 HTTP 的 PATCH 操作
@hero_router.patch("/update/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="英雄未找到！")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db


# 删除单个英雄id
@hero_router.post("/delete/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="该英雄未找到!")
    session.delete(hero)
    session.commit()
    return hero
