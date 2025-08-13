from typing import List
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# Field 主要用途:数据库索引 添加字段约束 设置默认值 zhujian
class WeaponBase(SQLModel):
    damage: int
    name: str = Field(index=True)
    type: str
    ammo: str


class Weapon(WeaponBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    eng_name: str


class WeaponPublic(WeaponBase):
    id: int


class WeaponCreate(WeaponBase):
    eng_name: str


class WeaponUpdate(WeaponBase):
    name: str | None = None
    damage: int | None = None
    type: str | None = None
    ammo: str | None = None
    eng_name: str | None = None


class WeaponUpdateReq(BaseModel):
    update_key: List[str]
    update_weapon: WeaponUpdate
