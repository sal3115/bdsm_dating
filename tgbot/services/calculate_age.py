from datetime import date, datetime


def calculateAge(birthDate):
    today = date.today()
    date_time_obj = datetime.strptime(str(birthDate), '%Y-%m-%d')
    age = today.year - date_time_obj.year -((today.month, today.day) < (date_time_obj.month, date_time_obj.day))
    return age


def test_date():
    today = datetime.today().date()
    print(today)
    print(type(today))


if __name__ == '__main__':
    test_date()