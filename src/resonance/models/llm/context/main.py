import sqlite3
import json
from ....tools.date import date_time

def get_context(ai: dict, data: dict, date="") -> list[dict]:
    try:
        if date:
            with open(f"context/{data['layers']['identity']['persona']['name']}/{date_time('date')}.context") as f:
                result = f.read()
            return json.loads(result)

        return []

    except FileNotFoundError:

        print(f"The context doesn't exist for the date: {date}, creating it...")
        context = []
        if layers := data.get('layers'):
            if identity_data := layers.get("identity"):
                    persona = identity_data["persona"]
                    context = [{"role": "system", "content": f"""You are now roleplaying {persona["name"]}. Embody her personality, behavior, and speech style consistently in every response. Stay in character at all times. Respond as {persona["name"]} would naturally respond in conversation. Do not mention being an AI, a language model, or that you are roleplaying. Do not narrate the user’s actions or thoughts. You may describe {persona["name"]}’s own actions, expressions, or tone briefly when appropriate."""}, {"role": "system", "content": ai["identity"].persona_format_prompt(persona)}]
        if output_rules := data.get("output_rules"):
            context.append({"role": "system", "content": output_rules})
        return context
