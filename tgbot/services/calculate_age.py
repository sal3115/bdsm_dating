from datetime import date, datetime


async def calculateAge(birthDate):
    today = date.today()
    date_time_obj = datetime.strptime(str(birthDate), '%Y-%m-%d')
    age = today.year - date_time_obj.year -((today.month, today.day) < (date_time_obj.month, date_time_obj.day))
    return age
