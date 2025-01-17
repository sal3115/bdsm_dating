
from yoomoney import Quickpay



async def paid_url(user_id, id_rate, amount):
    quickpay = Quickpay(
                receiver="410012030256059",
                quickpay_form="shop",
                targets="subscription_bot",
                paymentType="SB",
                sum=amount,
                label=f'{user_id}-{id_rate}-{amount}'
                )
    return quickpay.redirected_url



