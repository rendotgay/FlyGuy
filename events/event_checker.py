from datetime import datetime

# Holidays
def is_weed_day() -> bool:
    today = datetime.today()
    return today.month == 4 and today.day == 20

def is_christmas() -> bool:
    today = datetime.today()
    return today.month == 12 and today.day == 25

def is_halloween() -> bool:
    today = datetime.today()
    return today.month == 10 and today.day == 31

def is_april_fools() -> bool:
    today = datetime.today()
    return today.month == 4 and today.day == 1

def is_independence_day() -> bool:
    today = datetime.today()
    return today.month == 7 and today.day == 4

def is_new_years_eve():
    today = datetime.today()
    if (today.month == 12 and today.day == 30 and today.hour > 4) or (today.month == 12 and today.day == 31):
        return today.year + 1
    elif (today.month == 1 and today.day == 1 and today.hour < 7):
        return today.year
    else:
        return None

def is_new_years() -> bool:
    today = datetime.today()
    return (today.month == 12 and today.day == 31 and today.hour > 4) or (today.month == 1 and today.day == 1 and today.hour < 7)


# Birthdays
def is_flyguy_bday() -> bool:
    today = datetime.today()
    return today.month == 5 and today.day == 11

def is_ren_bday() -> bool:
    today = datetime.today()
    return today.month == 9 and today.day == 25

def is_bread_bday() -> bool:
    today = datetime.today()
    return today.month == 4 and today.day == 30