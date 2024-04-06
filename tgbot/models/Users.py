from sqlalchemy import Column, BigInteger, String, Integer, Boolean, ForeignKey, Date, inspect

import json

from tgbot.models.Base_model import Base


class Users(Base):
    __tablename__ = 'Users'

    user_id = Column(BigInteger, primary_key=True)
    status = Column(String, ForeignKey("status_user.title_status"))
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    phone_number = Column(String)
    e_mail = Column(String)
    gender = Column(String)
    birthday = Column(Date)
    country = Column( String )
    town = Column( String )
    confession = Column( String )
    church = Column( String )
    guarantor = Column(String)
    social_network = Column(String)
    video = Column(String)
    about_my_self = Column(String)
    partner_another_city = Column( Boolean )
    partner_another_town = Column( Boolean )
    partner_another_conf = Column( Boolean )
    min_age = Column(Integer)
    max_age = Column(Integer)
    awards = Column(String)
    moderation = Column(Boolean)
    time_reg = Column(Date)
    time_verif = Column(Date)
    last_time = Column(Date)
    active_day = Column(Integer)


    def __repr__(self):
        obj = {
            'user_id': self.user_id,
            'status': self.status,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'phone_number': self.phone_number,
            'e_mail': self.e_mail,
            'gender': self.gender,
            'birthday': self.birthday,
            'country': self.country,
            'town': self.town,
            'confession': self.confession,
            'church': self.church,
            'guarantor': self.guarantor,
            'social_network': self.social_network,
            'video': self.video,
            'about_my_self': self.about_my_self,
            'partner_another_city': self.partner_another_city,
            'partner_another_town': self.partner_another_town,
            'partner_another_conf': self.partner_another_conf,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'awards': self.awards,
            'moderation': self.moderation,
            'time_reg': self.time_reg,
            'time_verif': self.time_verif,
            'last_time': self.last_time,
            'active_day': self.active_day,

        }

        str_obj = json.dumps(obj)
        return str_obj




class PhotoTable(Base):
    __tablename__ = 'photo_table'

    id = Column(Integer , primary_key=True)
    id_user = Column(BigInteger, ForeignKey("Users.user_id"))
    photo_id = Column(String(255))
    unique_id = Column(String(255))
    is_first_photo = Column(Boolean)

    def __init__(self, id_user, photo_id, unique_id,is_first_photo):
        self.id_user = id_user
        self.photo_id = photo_id
        self.unique_id = unique_id
        self.is_first_photo = is_first_photo
    def __repr__(self):
        obj = {
            'id': self.id,
            'id_user': self.id_user,
            'photo_id' : self.photo_id,
        }
        str_obj = json.dumps(obj)
        return str_obj


class LikeDislikeTable(Base):
    __tablename__ = 'like_dislike_table'

    id = Column(Integer , primary_key=True)
    id_user = Column(BigInteger, ForeignKey("Users.user_id"))
    id_partner = Column(BigInteger)
    reaktion = Column(Boolean)

    def __init__(self, id_user, id_partner, reaktion):
        self.id_user = id_user
        self.id_partner = id_partner
        self.reaktion = reaktion

    def __repr__(self):
        obj = {
            'id': self.id,
            'id_user': self.id_user,
            'id_partner': self.id_partner,
            'reaktion': self.reaktion,
        }
        str_obj = json.dumps(obj)
        return str_obj


class ComplaintsTable( Base ):
    __tablename__ = 'complaints_table'

    id = Column( Integer, primary_key=True )
    id_user = Column( BigInteger, ForeignKey( "Users.user_id" ) )
    id_user_complaints = Column( BigInteger )
    complaints = Column( String )
    decision = Column(Boolean)

    def __init__(self, id_user, id_user_complaints, complaints, decision):
        self.id_user = id_user
        self.id_user_complaints = id_user_complaints
        self.complaints = complaints
        self.decision = decision

    def __repr__(self):
        obj = {
            'id': self.id,
            'id_user': self.id_user,
            'id_user_complaints': self.id_user_complaints,
            'complaints': self.complaints,
            'decision': self.decision,
        }
        str_obj = json.dumps( obj )
        return str_obj


class Reward_table( Base ):
    __tablename__ = 'reward_table'

    id = Column( Integer, primary_key=True )
    id_user = Column( BigInteger, ForeignKey( "Users.user_id" ) )
    reward = Column( String )
    date_reward = Column(Date)

    def __init__(self, id_user, reward, date_reward):
        self.id_user = id_user
        self.reward = reward
        self.date_reward = date_reward

    def __repr__(self):
        obj = {
            'id': self.id,
            'id_user': self.id_user,
            'reward': self.reward,
            'date_reward': self.date_reward,
        }
        str_obj = json.dumps( obj )
        return str_obj


class DifferentLinksTable( Base ):
    __tablename__ = 'different_links_table'

    id = Column( Integer, primary_key=True )
    link = Column( String )
    description = Column( String )

    def __init__(self, link, description):
        self.link= link
        self.description = description

    def __repr__(self):
        obj = {
            'id': self.id,
            'link': self.link,
            'description': self.description,
        }
        str_obj = json.dumps( obj )
        return str_obj


class RejectingVerification( Base ):
    __tablename__ = 'rejecting_verification'

    id = Column( Integer, primary_key=True )
    user_id = Column( BigInteger, ForeignKey( "Users.user_id" ) )
    description = Column( String )

    def __init__(self, user_id, description):
        self.user_id = user_id
        self.description = description

    def __repr__(self):
        obj = {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
        }
        str_obj = json.dumps( obj )
        return str_obj


class BlockUserDescription( Base ):
    __tablename__ = 'block_user_description'

    id = Column( Integer, primary_key=True )
    user_id = Column( BigInteger, ForeignKey( "Users.user_id" ) )
    description = Column( String )

    def __init__(self, user_id, description):
        self.user_id = user_id
        self.description = description

    def __repr__(self):
        obj = {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
        }
        str_obj = json.dumps( obj )
        return str_obj


class StatusUser(Base):
    __tablename__ = 'status_user'

    id = Column( Integer, primary_key=True )
    title_status = Column(String)
    description = Column(String)
    title_of_russia = Column( String )

    def __init__(self, title_status, title_of_russia, description):
        self.title_status = title_status
        self.title_of_russia = title_of_russia
        self.description = description
    def __repr__(self):
        obj = {
            'id': self.id,
            'title_status': self.title_status,
            'title_of_russia': self.title_of_russia,
            'description': self.description,
        }
        str_obj = json.dumps( obj )
        return str_obj