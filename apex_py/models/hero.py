from sqlmodel import Field, SQLModel


# 创建一个基类模型 该模型具有所有模型共享的字段
class HeroBase(SQLModel):
    age: int | None = Field(default=None, index=True)
    name: str = Field(index=True)
    backgroud_story: str
    describe: str


# 创建一个实际的表模型并添加在那些不总是在其他模型中的额外字段
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    real_name: str


# 创建一个公共数据模型
class HeroPublic(HeroBase):
    id: int


# 创建一个验证客户数据的模型
class HeroCreate(HeroBase):
    real_name: str


# 创建一个用于更新的数据模型
class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    real_name: str | None = None
    backgroud_story: str | None = None
    describe: str | None = None
