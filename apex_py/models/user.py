from sqlmodel import Field, SQLModel


class Userbase(SQLModel):
    name: str = Field(index=True)
    passwd: str = Field(index=True)
    phone: str = Field(index=True)


class User(Userbase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserPublic(Userbase):
    id: int


class UserUpdate(Userbase):
    name: str | None = None
    passwd: str | None = None
    phone: str | None = None
