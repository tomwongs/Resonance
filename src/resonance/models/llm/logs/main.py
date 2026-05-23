import os
from ....tools import date

def add_entry(msg: str) -> bool:
    filename = f"{date.date_time('date')}.log"
    # NEED SYNTAX CHECK
    #if not os.fileexist:
    #    with open(filename, 'x'): as file:
    #        file.write(msg)

    try: 
        with open(filename, 'a') as file:
            file.write(msg) 
        return True

    except Exception as e:
        print(f"\x1b[31m{e}\x1b[0m")
        return False
