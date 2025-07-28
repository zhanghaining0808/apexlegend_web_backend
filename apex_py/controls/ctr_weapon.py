# from typing import Annotated
# from fastapi import APIRouter, HTTPException, Query
# from sqlmodel import select

# from apex_py.db.db import SessionDep
# from apex_py.models.weapon import Weapon, WeaponPublic, WeaponUpdate


# weapon_router = APIRouter(prefix="/weapons")


# @weapon_router.post("/add", response_model=WeaponPublic)
# def create_weapon(weapon: Weapon, session: SessionDep):
#     session.add(Weapon)
#     session.commit()
#     session.refresh(Weapon)
#     return weapon


# # 利用limit和offset来对结果进行分页处理
# # 使用 response_model=list[HeroPublic] 确保正确地验证和序列化数据
# @weapon_router.get("/query", response_model=list[WeaponPublic])
# def read_all_weapons(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ):
#     weapons = session.exec(select(Weapon).offset(offset).limit(limit)).all()
#     return weapons


# # 用Public读取单个武器id
# @weapon_router.get("/query/{weapon_id}", response_model=WeaponPublic)
# def read_weapon(weapon_id: int, session: SessionDep):
#     weapon = session.get(Weapon, weapon_id)
#     if not weapon:
#         raise HTTPException(status_code=404, detail="武器未找到!")
#     return weapon


# @weapon_router.patch("/update/{weapon_id}", response_model=WeaponPublic)
# def update_weapon(weapon_id: int, weapon: WeaponUpdate, session: SessionDep):
#     weapon_db = session.get(Weapon, weapon_id)
#     if not weapon:
#         raise HTTPException(status_code=404, detail="武器未找到!")
#     weapon_data = weapon.model_dump(exclude_unset=True)
#     weapon_db.sqlmodel_update(weapon_data)
#     session.add(weapon_db)
#     session.commit()
#     session.refresh(weapon_db)
#     return weapon_db


# # 删除单个武器id
# @weapon_router.post("/delete/{weapon_id}")
# def delete_weapon(weapon_id: int, session: SessionDep):
#     weapon = session.get(Weapon, weapon_id)
#     if not weapon:
#         raise HTTPException(status_code=404, detail="该武器未找到!")
#     session.delete(weapon)
#     session.commit()
#     return weapon
