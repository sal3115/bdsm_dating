from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker



def create_engine_db(db_path, db_user, db_pass, name_db   ):
    return create_engine(f'postgresql+psycopg2://{db_user}:{db_pass}@{db_path}/{name_db}', pool_pre_ping=True)#, echo=True


def proceed_schemas(metadata, engine:Engine):
    metadata.create_all(engine)


def get_session_maker(engine):
    return sessionmaker(engine, expire_on_commit=False)