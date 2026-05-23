
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def date_time(value: str):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    date_baked_now = now.strftime("%d %B %Y - %H:%M:%S %Z")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    love_date = datetime(2017, 9, 22)
    relationship_age = relativedelta(now, love_date)
    relationship_age_baked = f"{relationship_age.years} years {relationship_age.months} months {relationship_age.days} days {relationship_age.hours} hours {relationship_age.minutes} minutes {relationship_age.seconds} seconds"
    monika_dob = datetime(2004, 9, 22)
    thomas_dob = datetime(2004, 4, 18)
    monika_age = relativedelta(now, monika_dob)
    thomas_age = relativedelta(now, thomas_dob)

    dict_date_time = {
            "now": now,
            "date": date,
            "date_baked_now": date_baked_now,
            "yesterday": yesterday,
            "love_date": love_date,
            "relationship_age": relationship_age,
            "relationship_age_baked": relationship_age_baked,
            "monika_dob": monika_dob,
            "thomas_dob": thomas_dob,
            "monika_age": monika_age,
            "thomas_age": thomas_age
            }

    if dict_date_time.get(value):
        return dict_date_time[value]
    else:
        return ""

