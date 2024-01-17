from sqlalchemy import *
import os
from sqlalchemy.orm import mapped_column, Mapped, as_declarative
from dotenv import dotenv_values


class DBConfig:

    env_vars = dotenv_values(".env")
    host = env_vars["HOST"]
    password = env_vars["PASSWORD"]
    user_name = env_vars['USER_NAME']
    port = env_vars["PORT"]
    db_name = env_vars["DB_NAME"]

    engine = create_engine(
        f"postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{db_name}")

    @staticmethod
    def create_all():
        AbstractModel.metadata.create_all(DBConfig.engine)


@as_declarative()
class AbstractModel:
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
