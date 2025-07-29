from sqlmodel import Field, SQLModel


class Userbase(SQLModel):
    # name作为标识，只允许存在一条用户名称相同的数据
    name: str = Field(index=True, unique=True)
    phone: str = Field(unique=True)
    passwd: str


class User(Userbase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserPublic(Userbase):
    id: int


class UserUpdate(Userbase):
    name: str | None = None
    passwd: str | None = None
    phone: str | None = None
