from sqlmodel import Field, SQLModel


class Stage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sname: str = Field(default=id, nullable=False, unique=True)
<<<<<<< HEAD
    isLocked: bool = Field(default=False, nullable=False)
    unlockPreconditionStars: int = Field(nullable=False)
=======
    is_locked: bool = Field(default=False, nullable=False)
    unlock_precondition_stars: int = Field(nullable=False)
>>>>>>> 6ed5138fce2e80597f984088e11bdf4a84aca43d
