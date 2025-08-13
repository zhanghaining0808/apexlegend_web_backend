from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from apex_py.db.db import SessionDep
from apex_py.middleware.check_auth import check_auth_M
from apex_py.models.response import ApexResponse
from apex_py.models.weapon import Weapon, WeaponUpdateReq


weapon_router = APIRouter(
    prefix="/api/weapons",
    dependencies=[Depends(check_auth_M)],
)


@weapon_router.post("/add", response_model=ApexResponse)
def create_weapon(weapon: Weapon, session: SessionDep):
    session.add(weapon)
    session.commit()
    session.refresh(weapon)
    return ApexResponse(data=weapon.model_dump(), msg="创建Apex武器成功")


@weapon_router.get("/query", response_model=ApexResponse)
def read_all_weapons(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    weapons = session.exec(select(Weapon).offset(offset).limit(limit)).all()
    return ApexResponse(data=list(weapons), msg="获取全部武器成功")


@weapon_router.get("/query/{weapon_id}", response_model=ApexResponse)
def read_weapon(weapon_id: int, session: SessionDep):
    weapon = session.get(Weapon, weapon_id)
    if not weapon:
        raise HTTPException(status_code=404, detail="武器未找到!")
    return ApexResponse(data=list(weapon), msg="读取单把武器成功")


@weapon_router.post("/update/{weapon_id}", response_model=ApexResponse)
def update_weapon(
    weapon_id: int, weapon_updata_req: WeaponUpdateReq, session: SessionDep
):
    find_weapon = session.get(Weapon, weapon_id)
    need_update_weapon = weapon_updata_req.update_weapon.model_dump()

    if not need_update_weapon:
        raise HTTPException(status_code=404, detail="武器新数据未找到!")
    if not find_weapon:
        raise HTTPException(status_code=404, detail="武器旧数据未找到!")

    old_weapon = find_weapon.model_dump()
    new_weapon = old_weapon

    for need_update_key in weapon_updata_req.update_key:
        print(need_update_key)
        if need_update_key in old_weapon.keys():
            new_weapon[need_update_key] = need_update_weapon[need_update_key]

    find_weapon.sqlmodel_update(new_weapon)
    session.commit()
    session.refresh(find_weapon)
    return ApexResponse(data=find_weapon.model_dump(), msg="更新单把武器成功")


@weapon_router.post("/delete/{weapon_id}", response_model=ApexResponse)
def delete_weapon(weapon_id: int, session: SessionDep):
    weapon = session.get(Weapon, weapon_id)
    if not weapon:
        raise HTTPException(status_code=404, detail="该武器未找到!")
    session.delete(weapon)
    session.commit()
    return ApexResponse(data=weapon.model_dump(), msg="武器已删除!")
