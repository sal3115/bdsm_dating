from sqlalchemy import Column, BigInteger, String, Integer, Boolean, ForeignKey, Date, inspect, Float, Sequence

import json

from tgbot.models.Base_model import Base


class Users(Base):
    __tablename__ = 'Users'
    id = Column(BigInteger, Sequence('id'), nullable=False)
    user_id = Column(BigInteger, primary_key=True)
    status = Column(String, ForeignKey("status_user.title_status"))
    first_name = Column(String)
    username = Column(String)
    gender = Column(String)
    birthday = Column(Date)
    city = Column( String )
    country = Column( String )
    about_my_self = Column(String)
    your_position = Column(String)
    partner_position = Column(String)
    practices = Column(String)
    interaction_format = Column(String)
    gender_partner = Column(String, default='woman')
    tabu = Column(String)
    partner_another_city = Column( Boolean )
    min_age = Column(Integer)
    max_age = Column(Integer)
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
            'username': self.username,
            'gender': self.gender,
            'birthday': self.birthday,
            'city': self.city,
            'about_my_self': self.about_my_self,
            'partner_another_city': self.partner_another_city,
            'partner_another_town': self.partner_another_town,
            'min_age': self.min_age,
            'max_age': self.max_age,
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
    date_reaktion = Column(Date)


    def __init__(self, id_user, id_partner, reaktion, date_reaktion):
        self.id_user = id_user
        self.id_partner = id_partner
        self.reaktion = reaktion
        self.date_reaktion = date_reaktion
    def __repr__(self):
        obj = {
            'id': self.id,
            'id_user': self.id_user,
            'id_partner': self.id_partner,
            'reaktion': self.reaktion,
            'date_reaktion': self.date_reaktion,
        }
        str_obj = json.dumps(obj)
        return str_obj


class DailyReactionTable(Base):
    __tablename__ = 'daily_reaction_table'

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


class ComplaintsTable( Base ): #жалоба
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
    title_status = Column(String, unique=True)
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


class PaidTable( Base ):
    __tablename__ = 'paid_table'

    id = Column( Integer, primary_key=True, autoincrement= True )
    user_id = Column( BigInteger, ForeignKey( "Users.user_id" ), unique=True )
    date_reg = Column( Date )
    date_before = Column( Date )

    def __init__(self, user_id, date_reg, date_before):
        self.user_id = user_id
        self.date_reg = date_reg
        self.date_before = date_before

    def __repr__(self):
        obj = {
            'id': self.id,
            'user_id': self.user_id,
            'date_reg': self.date_reg,
            'date_before': self.date_before,
        }
        str_obj = json.dumps( obj )
        return str_obj

class PriceSubscription( Base ):
    __tablename__ = 'price_subs_table'
    id = Column( Integer, primary_key=True, autoincrement=True )
    title = Column( String, nullable=False)
    price = Column( Float, nullable=False )
    number_of_days = Column(Integer, nullable=False)
    new_price = Column(Float)
    def __init__(self, title=None, price=None, new_price=None, number_of_days=None):
        self.title = title
        self.price = price
        self.number_of_days = number_of_days
        self.new_price = new_price

    def __repr__(self):
        obj = {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'number_of_days': self.number_of_days,
            'new_price': self.new_price,
        }
        str_obj = json.dumps( obj )
        return str_obj


class ResendGroupAndChannel( Base ):
    __tablename__ = 'resend_group_channel_table'
    id = Column( Integer, primary_key=True, autoincrement=True )
    id_admin = Column( BigInteger)
    id_channel_group = Column( BigInteger)
    title_channel_group = Column(String)
    type_channel_group = Column(String)
    url = Column(String)


    def __init__(self, id_admin=None, id_channel_group=None, title_channel_group=None, type_channel_group=None, url=None):
        self.id_admin = id_admin
        self.id_channel_group = id_channel_group
        self.title_channel_group = title_channel_group
        self.type_channel_group = type_channel_group
        self.url = url
    def __repr__(self):
        obj = {
            'id_admin': self.id_admin,
            'id_channel_group': self.id_channel_group,
            'title_channel_group': self.title_channel_group,
            'type_channel_group': self.type_channel_group,
            'url': self.url
        }
        str_obj = json.dumps( obj )
        return str_obj


class FeaturesResendGroupAndChannel( Base ):
    __tablename__ = 'features_resend_channel_table'
    id = Column( Integer, primary_key=True, autoincrement=True )
    id_channel_group = Column( BigInteger,ForeignKey( "resend_group_channel_table.id" )  )
    thread_message_id = Column( BigInteger )
    features = Column( String )

    def __init__(self,  id_channel_group=None, thread_message_id=None, features=None):
        self.id_channel_group = id_channel_group
        self.features = features
        self.thread_message_id = thread_message_id

    def __repr__(self):
        obj = {
            'id_channel_group': self.id_channel_group,
            'features': self.features,
            'thread_message_id': self.thread_message_id,
        }
        str_obj = json.dumps( obj )
        return str_obj

class ResendFreePlatform(Base):
    __tablename__ = 'resend_free_platform_table'
    id = Column( Integer, primary_key=True, autoincrement=True )
    user_id = Column( BigInteger, ForeignKey( "Users.user_id" ))
    id_platform = Column( BigInteger, ForeignKey( "resend_group_channel_table.id" ) )
    message_id = Column( BigInteger )
    features = Column( String )
    anonymous = Column(Boolean)
    def __init__(self, user_id=None, id_platform=None, message_id=None, features=None, anonymous=None):
        self.user_id = user_id
        self.id_platform = id_platform
        self.features = features
        self.message_id = message_id
        self.anonymous = anonymous
    def __repr__(self):
        obj = {
            'user_id': self.user_id,
            'id_platform': self.id_platform,
            'features': self.features,
            'message_id': self.thread_message_id,
            'anonymous': self.anonymous
        }
        str_obj = json.dumps( obj )
        return str_obj
