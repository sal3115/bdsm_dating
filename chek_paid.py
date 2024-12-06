from hypercorn import Config
from tgbot.config import load_config
import hashlib
from quart import Quart, request

app = Quart(__name__)
@app.route( '/' )
def hello():
    return 'Hello, World! this application runing on 192.168.0.105'
@app.route( '/webhook', methods=["POST"]  )
async def webhook_check_main():
    webhook_answer = await request.form
    webhook_answer = webhook_answer.to_dict()
    config = load_config( ".env" )
    secret_str = config.yoomoney.secret_word_yoomoney
    str_in_hash = str(
        f'{webhook_answer["notification_type"]}&{webhook_answer["operation_id"]}&{webhook_answer["amount"]}&'
        f'{webhook_answer["currency"]}&{webhook_answer["datetime"]}&{webhook_answer["sender"]}&'
        f'{webhook_answer["codepro"]}&{secret_str}&{webhook_answer["label"]}' )
    hash_object = hashlib.sha1( str_in_hash.encode() )
    hash_main = hash_object.hexdigest()
    hash_yoomoney = webhook_answer['sha1_hash']
    unaccepted = webhook_answer['unaccepted']
    if hash_main == hash_yoomoney:
        if not unaccepted:
            label = webhook_answer['label'].split( '-' )
            user_id = label[0]
            title = label[1]
            price = label[2]

    else:
        return '500'
    return 'Hello,webhook!'
