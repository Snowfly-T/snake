from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uname: str = Field(default=id, nullable=False, unique=True)
    password: str = Field(nullable=False, max_length=20, min_length=8)
    phoneNumber: str = Field(nullable=False, min_length=11, max_length=11)
    level: int = Field(min_items=1, nullable=False)
    experience: int = Field(nullable=False)
    commonMoney: int = Field(nullable=False, min_items=0)
    specialMoney: int = Field(nullable=False, min_items=0)
    totalStars: int=Field(default=0,nullable=False)
    rank: str = "最强青铜IV"
    score: int = Field(default=0, min_items=0, max_items=100)