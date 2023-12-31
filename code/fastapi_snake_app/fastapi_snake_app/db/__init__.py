import pkgutil

from sqlalchemy.orm import declarative_base
from sqlmodel import SQLModel, create_engine

from fastapi_snake_app.main import app

# SQLAlchemy specific code, as with any other app
DATABASE_URL = 'mysql://code_snake:code_snake@snowflyt-out.mysql.rds.aliyuncs.com:3306/code_snake'

Base = declarative_base()

# Import models
__path__ = pkgutil.extend_path(__path__, __name__)
for imp, module, ispackage in pkgutil.walk_packages(path=__path__, prefix=f'{__name__}.'):
    __import__(module)

engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
