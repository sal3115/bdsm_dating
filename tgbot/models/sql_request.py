import asyncio
import datetime
import logging

import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import select, and_, or_, not_, update, func, Table, inspect, create_engine, exc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased, Session

from tgbot import config
from tgbot.models.Base_model import Base
from tgbot.models.Users import Users, LikeDislikeTable, PhotoTable, ComplaintsTable, \
    RejectingVerification, BlockUserDescription, PaidTable, PriceSubscription
from tgbot.models.engine import create_engine_db, get_session_maker

logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )


async def insert_users(session, params, value = None):
    user_1 = Users(
    user_id= params['user_id'],
    status = 'user',
    first_name =params['name'],
    username = params['user_name'],
    gender = params['gender'],
    birthday =params['birthday'],
    city = params['city'],
    about_my_self = params['about_me'],
    partner_another_city =params['partner_another_city'],
    min_age = params['min_age'],
    max_age = params['max_age'],
    moderation = False,
    time_reg = datetime.datetime.today().date(),
    time_verif = None,
    last_time = datetime.datetime.today().date(),
    active_day = 1,
    )
    with session() as ses:
        with ses.begin():
            try:
                ses.add(user_1)
            except IntegrityError as e:
                logging.info(msg=[e.args, e])
                pass


async def insert_like_dis(session, user_id, partner_id, reaction:bool=False):
    insert_ld_table = LikeDislikeTable(id_user=user_id, id_partner = partner_id, reaktion=reaction)
    with session() as ses:
        with ses.begin():
            try:
                ses.add(insert_ld_table)
            except IntegrityError as e:
                logging.info(msg=[e.args, e])
                pass


async def insert_complaints(session, id_user, id_user_complaints, complaints, decision=False):
    insert_complaints_table = ComplaintsTable(id_user=id_user, id_user_complaints = id_user_complaints,
                                              complaints=complaints, decision=decision)
    with session() as ses:
        with ses.begin():
            try:
                ses.add(insert_complaints_table)
            except IntegrityError as e:
                logging.info(msg=[e.args, e])
                pass


async def insert_photo(session, user_id, photo_id, unique_id = None ,is_first_photo=False):
    request_photo = PhotoTable(id_user=user_id, photo_id=photo_id, unique_id=unique_id ,is_first_photo=False)
    with session() as ses:
        with ses.begin():
            ses.add(request_photo)


async def insert_rejecting_verification(session,user_id, description):
    request = RejectingVerification( user_id=user_id, description=description )
    with session() as ses:
        with ses.begin():
            ses.add( request )


async def insert_block_user_description(session,user_id, description):
    request = BlockUserDescription( user_id=user_id, description=description )
    with session() as ses:
        with ses.begin():
            ses.add( request )

class NumberOfDays(BaseException):
    pass

async def update_paid_subscription(session, user_id, number_of_days):
    request = select( PaidTable.date_before ).where( PaidTable.user_id == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            date_subs = answer2[0]['date_before']
            if int( number_of_days ) == 7:
                date_before = date_subs + datetime.timedelta( 7 )
            elif int( number_of_days ) == 30:
                date_before = date_subs + relativedelta( months=+1 )
            else:
                raise NumberOfDays
            stmt = update( PaidTable ).where( PaidTable.user_id == user_id ).values( date_before=date_before )
            ses.execute( stmt )


async def insert_paid_subscription(session,user_id, number_of_day):
    today =  datetime.datetime.now().date()
    if int( number_of_day ) == 7:
        date_before = today + datetime.timedelta( 7 )
    elif int( number_of_day ) == 30:
        date_before = today + relativedelta( months=+1 )
    else:
        raise NumberOfDays
    request = PaidTable( user_id=user_id, date_reg=today, date_before = date_before )
    with session() as ses:
        try:
            with ses.begin():
                ses.add( request )
        except exc.IntegrityError:
            await update_paid_subscription(session=session, user_id=user_id, number_of_days=number_of_day)



async def select_all_users_mailing(session):
    request = select(Users.user_id).where(
        or_(Users.status == 'user', Users.status == 'hidden_user', Users.status == 'exit_user')
    )

    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_user_anketa(session, user_id):
    with session() as ses:
        with ses.begin():
            user = ses.query( Users ).filter( Users.user_id == user_id ).first()
            partner_another_city = user.partner_another_city
            min_age = user.min_age
            max_age = user.max_age

            today = datetime.datetime.today()
            min_birthday = today - datetime.timedelta( days=(365 * max_age) )
            max_birthday = today - datetime.timedelta( days=(365 * min_age + 1) )

            request = select(
                Users.user_id, Users.first_name, Users.username, Users.birthday, Users.city,
                 Users.last_time
            ).filter(
                Users.user_id != user_id,
                ~Users.user_id.in_(
                    select( LikeDislikeTable.id_partner ).filter( LikeDislikeTable.id_user == user_id )
                ),
                Users.gender != select( Users.gender ).where( Users.user_id == user_id ),
                Users.moderation == True,
                Users.birthday <= max_birthday,  # Добавляем фильтр на максимальный возраст
                Users.birthday >= min_birthday,
                Users.status == "user",
            )

            if partner_another_city:
                request = request.where(
                        Users.partner_another_city == True,
                )
            if not partner_another_city:
                request = request.where(
                    and_(
                        Users.city == user.city,
                        or_(
                            Users.partner_another_city == False,
                            Users.partner_another_city == True
                        )
                    )
                )

            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_user_profile_like(session, user_id):
    request = select(*[col for col in Users.__table__.c]
    ).filter(
        Users.user_id != user_id,
        Users.user_id.in_( select( LikeDislikeTable.id_partner ).where( and_(
        LikeDislikeTable.id_user == user_id,
        LikeDislikeTable.reaktion == True
    ) ) ),
        Users.gender != select( Users.gender ).where( Users.user_id == user_id )
    )

    with session() as ses:
        with ses.begin():
            answer = ses.execute(request)
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2




async def select_user_profile_like_me(session, user_id):
    photo_subquery = (
        select(PhotoTable.id_user)
        .filter(and_(PhotoTable.id_user == Users.user_id, PhotoTable.is_first_photo == True))
        .limit(1)
    )

    liked_users_subquery = (
        select(LikeDislikeTable.id_user)
        .where(and_(
            LikeDislikeTable.id_partner == user_id,
            LikeDislikeTable.reaktion == True  # Assuming 1 is for like
        ))
    )

    reacted_users_subquery = (
        select(LikeDislikeTable.id_partner)
        .where(and_(
            LikeDislikeTable.id_user == user_id,
            LikeDislikeTable.reaktion.in_([True,False])  # Assuming 1 is for like and 2 is for dislike
        ))
    )

    request = select(*[col for col in Users.__table__.c]
    ).filter(
        Users.user_id != user_id,
        Users.user_id.in_(liked_users_subquery),  # Exclude users who have liked the current user
        ~Users.user_id.in_(reacted_users_subquery)  # Exclude users to whom the current user has reacted
    )

    request = request.where(Users.user_id.in_(photo_subquery))

    with session() as ses:
        with ses.begin():
            answer = ses.execute(request)
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2



# async def select_user_profile_like_me(session, user_id):
#     photo_subquery = (
#         select( PhotoTable.id_user )
#         .filter( and_( PhotoTable.id_user == Users.user_id, PhotoTable.is_first_photo == True ) )
#         .limit( 1 )
#     )
#     request = select(
#         Users.user_id, Users.first_name, Users.last_name, Users.username, Users.birthday, Users.country,
#         Users.town, Users.confession, Users.last_time, Users.awards
#     ).filter(
#         Users.user_id != user_id,
#         Users.user_id.in_(select(LikeDislikeTable.id_user).where(and_(
#             LikeDislikeTable.id_partner == user_id,
#             LikeDislikeTable.reaktion == 1
#         ))),
#         Users.gender != select(Users.gender).where(Users.user_id == user_id)
#     )
#     request = request.where( Users.user_id.in_( photo_subquery ) )
#     with session() as ses:
#         with ses.begin():
#             answer = ses.execute(request)
#             answer2 = [dict(r._mapping) for r in answer.fetchall()]
#             return answer2

async def select_user_profile_not_interest(session, user_id):
    request = select(*[col for col in Users.__table__.c]
    ).filter(
        Users.user_id != user_id,
        Users.user_id.in_( select( LikeDislikeTable.id_partner ).where( and_(
            LikeDislikeTable.id_user == user_id,
            LikeDislikeTable.reaktion == False
        ) ) ),
        Users.gender != select( Users.gender ).where( Users.user_id == user_id )
    )

    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_user_profile_mutual_interest(session, user_id):
    request = select(*[col for col in Users.__table__.c]
    ).filter(
        and_(
            Users.user_id.in_(select(LikeDislikeTable.id_user).where(and_(
                LikeDislikeTable.id_partner == user_id,
                LikeDislikeTable.reaktion == True
            ))),
            Users.user_id.in_(select(LikeDislikeTable.id_partner).where(and_(
                LikeDislikeTable.id_user == user_id,
                LikeDislikeTable.reaktion == True
            ))),
            Users.gender != select(Users.gender).where(Users.user_id == user_id)
        )
    )

    with session() as ses:
        with ses.begin():
            answer = ses.execute(request)
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2

async def select_check_mutual_interest(session, user_id, partner_id):
    request = select(LikeDislikeTable.id_user).where(
        and_(LikeDislikeTable.id_user == partner_id, LikeDislikeTable.id_partner==user_id),
    ).where(LikeDislikeTable.reaktion == True)
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2
async def select_column_data(*args, session, user_id):
    users_table = Users.__table__
    columns = [getattr(users_table.c, column_name) for column_name in args]
    query = select(*columns).where(users_table.c.user_id == user_id)
    with session() as ses:
        with ses.begin():
            answer = ses.execute(query)
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2


async def select_user(session, user_id):
    request = select(*[col for col in Users.__table__.c]).where( Users.user_id == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_user_name(session, user_id):
    request = select(Users.username).where( Users.user_id == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request)
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_user_anketa_verefication(session):
    request = select(*[col for col in Users.__table__.c]).filter( and_(Users.moderation == False,
                                                                       Users.status != 'exit_user',
                                                                       Users.status != 'delete_user',
                                                                       Users.status != 'moderator',
                                                                       Users.status != 'admin',
                                                                       Users.status != 'delete_user',
                                                                       Users.status != 'ver_user',
                                                                       )
                                                                )
    with session() as ses:
        with ses.begin():
            answer = ses.execute(request)
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2


# async def get_Confessions(session):
#     request = select(Confessions.id , Confessions.name)
#     with session() as ses:
#         with ses.begin():
#             answer = ses.execute( request )
#             return answer.all()


async def select_photo(session, user_id):
    request = select( PhotoTable.id_user, PhotoTable.photo_id, PhotoTable.is_first_photo ).where( PhotoTable.id_user == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_first_photo(session, user_id):
    request = select( PhotoTable.id_user, PhotoTable.photo_id, PhotoTable.unique_id ).where( PhotoTable.id_user == user_id ).where(
        PhotoTable.is_first_photo == True)
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_video_card(session, user_id):
    request = select( Users.video ).where(Users.user_id == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_moderation_user_id(session):
    request = select(Users.user_id).where(Users.status == 'moderator')
    with session() as ses:
        with ses.begin():
            answer = ses.execute(request)
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2


async def select_complaints(session):
    request = select(*[col for col in ComplaintsTable.__table__.c]).where(ComplaintsTable.decision==False)
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_complaints_join(session, user_id, complaints_user_id):
    # Создаем псевдонимы для таблицы Users
    user = aliased( Users )
    complaints_user = aliased( Users )
    # Составляем запрос
    request = select(
        user.first_name.label( 'user_first_name' ),
        user.last_name.label( 'user_last_name' ),
        user.username.label( 'user_username'),
        complaints_user.first_name.label( 'complaints_user_first_name' ),
        complaints_user.last_name.label( 'complaints_user_last_name' ),
        complaints_user.username.label('complaints_user_username'),
        ComplaintsTable.complaints
    ).join( user, ComplaintsTable.id_user == user.user_id ).join(
        complaints_user, ComplaintsTable.id_user_complaints == complaints_user.user_id
    ).filter(
        ComplaintsTable.id_user == user_id,
        ComplaintsTable.id_user_complaints == complaints_user_id
    )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


#поиск юзеров по имени и фамилии пока не используется
async def select_search_users(session, name=None, lastname=None, first_letter_lastname=None):
    query = select( Users.user_id,Users.first_name,Users.last_name )
    if name:
        query = query.filter( Users.first_name.ilike( f"%{name}%" ) )
    if lastname:
        query = query.filter( Users.last_name.ilike( f"%{lastname}%" ) )
    if first_letter_lastname:
        query = query.filter( Users.last_name.ilike( f"{first_letter_lastname}%" ) )
    with session() as ses:
        with ses.begin():
            answer = ses.execute(query)
            logging.info(['------------------', answer])
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2

async def select_search_user_ids(session, user_id):
    request = select(
        Users.user_id, Users.first_name, Users.last_name, Users.username, Users.birthday, Users.country,
        Users.town, Users.confession, Users.last_time, Users.awards
    ).where(Users.user_id == user_id)
    with session() as ses:
        with ses.begin():
            answer = ses.execute(request)
            answer2 = [dict(r._mapping) for r in answer.fetchall()]
            return answer2


async def select_rejection_user(session, user_id):
    request = select(RejectingVerification.description).where( RejectingVerification.user_id == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request)
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_block_user_description(session, user_id):
    request = select(BlockUserDescription.description).where( BlockUserDescription.user_id == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request)
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2

async def select_paid(session, user_id):
    request = select(*[col for col in PaidTable.__table__.c]).where( PaidTable.user_id == user_id )
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request)
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def select_price_subscription(session):
    request = select(*[col for col in PriceSubscription.__table__.c])
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request)
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2


async def update_first_photo(session, user_id, photo_id ,first_photo = True):
    stmt = update( PhotoTable ).where(and_(PhotoTable.id_user == user_id, PhotoTable.photo_id == photo_id)).values(
        is_first_photo=first_photo )
    with session() as ses:
        with ses.begin():
            ses.execute( stmt )


async def update_moderation(session, user_id,moderation: bool = True):
    with session() as ses:
        with ses.begin():
            user = ses.query(Users).filter(Users.user_id == user_id).first()
            user.moderation = moderation
            ses.add(user)


async def update_user_info(session, user_id, **kwargs):
    stmt = update( Users ).where( Users.user_id == user_id ).values( **kwargs )
    with session() as ses:
        with ses.begin():
            ses.execute( stmt )


async def update_active_day(session, user_id):
    with session() as ses:
        with ses.begin():
            user = ses.query( Users ).filter( Users.user_id == user_id ).first()
            if user:
                # Увеличение счетчика активности пользователя
                user.active_day += 1
                # Обновление записи в базе данных
                ses.commit()


async def update_complaint_decision(session, complaint_user_id, **kwargs):
    stmt = update( ComplaintsTable ).where( ComplaintsTable.id_user_complaints == complaint_user_id ).values( **kwargs )
    with session() as ses:
        with ses.begin():
            ses.execute( stmt )



import pandas as pd

async def download_database(session):
    session = session()
    inspector = inspect(session.bind)
    table_names = inspector.get_table_names()
    for table_name in table_names:
        metadata = inspector.get_columns(table_name)
        column_names = [column['name'] for column in metadata]
        ModelClass = Base.metadata.tables[table_name]
        query = session.query(ModelClass)
        result = query.all()
        df = pd.DataFrame(result, columns=column_names)
        file_name = f"save_db/{table_name}.xlsx"
        df.to_excel( file_name )
    session.close()


async def delete_photo_in_table(session, user_id, unique_id):
    with session() as ses:
        with ses.begin():
            ses.query( PhotoTable ).filter_by( id_user=user_id, unique_id=unique_id ).delete()


async def delete_reaction(session, user_id, id_partner):
    with session() as ses:
        with ses.begin():
            ses: Session
            request = ses.query( LikeDislikeTable ).filter_by( id_user = user_id, id_partner=id_partner).delete()


async def delete_rejecting_verification(session, user_id):
    with session() as ses:
        with ses.begin():
            ses: Session
            request = ses.query( RejectingVerification ).filter_by( user_id=user_id).delete()


async def delete_block_user_description(session, user_id):
    with session() as ses:
        with ses.begin():
            ses: Session
            request = ses.query( BlockUserDescription ).filter_by( user_id=user_id).delete()



async def delete_paid(session, user_id):
    with session() as ses:
        with ses.begin():
            ses: Session
            request = ses.query( PaidTable ).filter_by( user_id=user_id).delete()