from sqlmodel import Field, SQLModel


class WeaponBase(SQLModel):
    damage: int | None = Field(default=None, index=True)
    name: str = Field(index=True)


# extended_mag:扩展弹夹
# optic:倍镜
# standard_stick:标准枪托
# barrel_stabilizer:枪管稳定器
class Weapon_Attachment_Slots:
    extended_mag: bool
    optic: bool
    standard_stick: bool
    barrel_stabilizer: bool


# 创建一个实际的表模型并添加在那些不总是在其他模型中的额外字段
class Weapon(WeaponBase, Weapon_Attachment_Slots, table=True):
    id: int | None = Field(default=None, index=True)
    type: str
    ammo: str


class WeaponPublic(WeaponBase):
    id: int


class WeaponCreate(WeaponBase):
    type: str
    ammo: str


class WeaponUpdate(WeaponBase, Weapon_Attachment_Slots):
    name: str | None = None
    damage: int | None = None
    type: str | None = None
    ammo: str | None = None
    extended_mag: bool | None = None
    optic: bool | None = None
    standard_stick: bool | None = None
    barrel_stabilizer: bool | None = None
