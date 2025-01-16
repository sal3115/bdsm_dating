from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    db_user: str
    db_pass: str
    db_name: str

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    id_group: int
    id_channel: int
    other_params: str = None


@dataclass
class Yookassa:
    yootoken: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    yootoken: Yookassa




def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            db_user=env.str( 'DB_USER' ),
            db_pass=env.str( 'DB_PASS' ),
            db_name=env.str( 'DB_NAME' ),

        ),
        yootoken = Yookassa(
            yootoken = env.str('YOOTOKEN')
        ),
        misc=Miscellaneous(
            id_group=env.int('ID_GROUP'),
            id_channel=env.int('ID_CHANNEL')
        )
    )
