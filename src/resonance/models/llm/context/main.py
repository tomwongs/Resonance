import sqlite3
import json

def get_context(date="") -> list:
    try:
        if date:
            with open(f"{date}.context") as f:
                result = f.read()
            return json.loads(result)

        return []

    except FileNotFoundError:
        print(f"\x1b[31mThe context doesn't exist for the date: {date}\x1b[0m")

    except Exception as e:
        print(f"\x1b[31m{e}\x1b[0m")

    return []
