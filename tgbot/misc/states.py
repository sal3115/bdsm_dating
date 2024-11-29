# состояния для начала общения с ботом
from aiogram.dispatcher.filters.state import StatesGroup, State


class FSM_hello(StatesGroup):
    your_name = State()
    your_gender = State()
    your_date_of_birth = State()
    your_city = State()
    your_position = State()
    partner_position = State()
    your_practice = State()
    your_tabu = State()
    your_about_me = State()
    your_photo = State()
    min_age = State()
    max_age= State()
    another_city = State()
    interaction_format = State()
    finish = State()
    choice_partner = State()



class EditProfile(StatesGroup):
    first_edit_profile_state = State()
# текст вопроса про Почту
    email_state = State()
# ловим почту спрашивам про телефон
    phone_state = State()
# ловим ответ на телефон и отправляем запрос по соцсетям
    social_network_state = State()
# ловим ответ про соц.сети запрос страны
    country_state = State()
# ловим страну спрашиваем город
    city_state = State()
# ловим город спрашиваем конфесию
    confession_state = State()
# ловим новую конфесию
    confession_new_state = State()
# ловим выбор конфессии, задаем вопрос про название церкви
    church_state = State()
# принимаем название церкви спашиваем анкеты другого города
    profiles_another_city_state = State()
# принимаем анкеты другого города спашиваем анкеты другой страны
    profiles_another_country_state = State()
# принимаем анкеты другой страны спашиваем анкеты другой конфессии
    profiles_another_confession_state = State()
# принимаем анкеты другой конфессии спашиваем Минимальный подходящий возраст
    min_age_state = State()
# принимаем Минимальный подходящий возраст спашиваем максимальный подходящий возраст
    max_age_state = State()
# принимаем максимальный подходящий возраст завершающий этап
    finish_state = State()


class EditOther(StatesGroup):
    #состояния для изменения о себе
    about_me_state = State()
    # состояния для изменения фото
    my_photo_state = State()
    # состояния для изменения видеовизитки
    my_video_card_state = State()
    name_state = State()
    city_state = State()
    practice_state = State()
    tabu_state = State()
    birthday_state = State()
    another_city_state = State()
    interaction_format_state = State()
    min_age_state = State()
    max_age_state = State()


class UserModeraion(StatesGroup):
    no_verification_state = State()
    write_state = State()

class ComplaintsUser(StatesGroup):
    complaints_state = State()

class RewardUser(StatesGroup):
    reward_id_state = State()
    reward_state = State()
    reward_confirm_state = State()

    return_reward_id_state = State()
    return_reward_state = State()
    return_reward_confirm_state = State()


class AppointRemoveModerator(StatesGroup):
    appoint_id_state = State()
    appoint_confirm_state = State()

    remove_id_state = State()
    remove_confirm_state = State()


class EditLink(StatesGroup):
    description_state = State()
    link_state = State()


class NewLink(StatesGroup):
    description_state = State()
    link_state = State()


class RecommendationsState(StatesGroup):
    search_first_name_state = State()
    search_last_name_state = State()
    search_first_last_name_state = State()


class MailingState(StatesGroup):
    mailing_state = State()


class SearchUser(StatesGroup):
    search_user_state = State()


class BlockUser(StatesGroup):
    block_user_state = State()

class EditUserModeration(StatesGroup):
    first_name_state = State()
    last_name_state = State()