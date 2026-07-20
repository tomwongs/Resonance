
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def date_time(value: str):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    date_baked_now = now.strftime("%d %B %Y - %H:%M:%S %Z")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    dict_date_time = {
            "now": now,
            "date": date,
            "date_baked_now": date_baked_now,
            "yesterday": yesterday,
            }

    if dict_date_time.get(value):
        return dict_date_time[value]
    else:
        return ""

