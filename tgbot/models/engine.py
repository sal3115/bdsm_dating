from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker



def create_engine_db(path):
    return create_engine(f'sqlite:///{path}', pool_pre_ping=True)


def proceed_schemas(metadata, engine:Engine):
    metadata.create_all(engine)


def get_session_maker(engine):
    return sessionmaker(engine, expire_on_commit=False)