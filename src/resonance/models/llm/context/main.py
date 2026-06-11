import sqlite3
import json
from ..prompt_builder import persona_format_prompt
from ....tools.date import date_time

def get_context(data: dict, date="") -> list:
    try:
        if date:
            with open(f"context/{data['layers']['identity']['persona']['name']}/{date_time('date')}.context") as f:
                result = f.read()
            return json.loads(result)

        return []

    except FileNotFoundError:

        print(f"\x1b[31mThe context doesn't exist for the date: {date}\x1b[0m")
        if layers := data.get('layers'):
            if identity_data := layers.get("identity"):
                return [{"role": "system", "content": persona_format_prompt(identity_data["persona"])}]

    return []


def change_system_prompt(file: str, data: dict, new_prompt: str):
    context = get_context(data, date_time("date")) 
    context[0] = {"role": "system", "content": new_prompt}

    with open(file, 'w') as f:
        f.write(json.dumps(context))

    return 
