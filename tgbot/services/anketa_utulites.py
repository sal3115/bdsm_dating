# проверка на правильность написания Имени или Фамилии (на кириллицу)
import re


async def checking_russian_letters(russian_letters):
    text = russian_letters.lower()
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя- '
    check = True
    for a in text:
        if a not in alphabet:
            check = False
    return check

async def check_mail(s):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pat,s):
        return True
    else:
        return False
# проверка на правильность ДАТЫ
async def check_manual_date(manual_date):
    check = True
    list_date = manual_date.split('-')
    if len(manual_date) != 10:
        check = False
    if len(list_date) != 3 or len(list_date[0]) != 2 or len(list_date[1]) != 2 or len(list_date[2]) != 4:
        check = False
    if manual_date.replace('-', '').isdigit() == False:
        check = False
    print(check)
    return check



def check_url(s):
    pat = r'\b[-a-zA-Z0-9@:%_\+.~#?&\/=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&\/=]*)?\b'
    if re.match(pat,s):
        return True
    else:
        return False



if __name__ == '__main__':
    irl = check_url('gjpap.ri')
    print(irl)

