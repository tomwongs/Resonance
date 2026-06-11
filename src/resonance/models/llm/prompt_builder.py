import json



def is_correct_llm_data(data={"provider":"", "model":""}):
    if not data.get("provider"):
        error = "\x1b[31mMissing a provider.\x1b[0m"
        print(error)
        return False

    if not data.get("model"):
        error = "\x1b[31mMissing a model.\x1b[0m"
        print(error)
        return False

    return True

def output_format_prompt(required_elements: dict):
    preprompt = "# How your output should be structured\n"
    preprompt += "Your output should STRICTLY ALWAYS be ONLY a JSON format with this structure, no backticks, no asterisks before or after the JSON, the following JSON structure is IMPERATIVE to respect:\n"
    preprompt += json.dumps(required_elements)
    return preprompt

def persona_format_prompt(persona: dict) -> str:
    system = ""

    if not persona["name"] or not persona["personality"]:
        print("\x1b[31mPlease provide a Name and a Personality for the AI.\x1b[0m")
        return ""

    system += f"""You are now roleplaying {persona["name"]}. Embody her personality, behavior, and speech style consistently in every response.
Stay in character at all times. Respond as {persona["name"]} would naturally respond in conversation. Do not mention being an AI, a language model, or that you are roleplaying.
Do not narrate the user’s actions or thoughts. You may describe {persona["name"]}’s own actions, expressions, or tone briefly when appropriate.
"""

    system += f"""
# {persona["name"].title()}'s description 
{persona["description"]}

# {persona["name"].title()}'s personality
{persona["personality"]}
"""
    
    if persona.get("traits"):
        system += f"""
# {persona["name"].title()}'s personality traits
- {", ".join(persona['traits'])}
"""

    if persona.get("speech_style"):
        system += f"""
# {persona["name"].title()}'s speech style
- {persona['speech_style']}
"""

    if persona.get("values"):
        system += f"""
# {persona["name"].title()}'s core values
- {", ".join(persona['values'])}
"""

    if persona.get("rules"):
        system += f"""
# You must follow these rules:
- {", ".join(persona['rules'])}
"""

    if other_info := persona.get("other_info"):
        for oinfo in other_info:
            system += f"""
# {oinfo["title"]}
{oinfo["content"]}
"""

    if persona.get("output_rules"):
        system += f"""
# How your output should be structured
{persona["output_rules"]}
"""

    return system



