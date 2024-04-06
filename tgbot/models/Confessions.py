from sqlalchemy import Column, BigInteger, String, Integer, Boolean, VARCHAR

import json

from tgbot.models.Base_model import Base


class Confessions(Base):
    __tablename__ = 'Confessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    status = Column(Boolean)

    def __init__(self, name=None, status=True):
        self.name = name
        self.status = status


    def __repr__(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'status': self.status,

        }
        str_obj = json.dumps(obj)
        return str_obj
