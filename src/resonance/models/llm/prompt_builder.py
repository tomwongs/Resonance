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

    system += f"""
# Your Persona
You are {persona["name"]}
{persona["description"]}

# Personality
{persona["personality"]}
"""
    
    if persona.get("traits"):
        system += f"""
# Personality Traits
- {", ".join(persona['traits'])}
"""

    if persona.get("speech_style"):
        system += f"""
# Speech style
- {persona['speech_style']}
"""

    if persona.get("values"):
        system += f"""
# Core Values
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
# Output Rules
{persona["output_rules"]}
"""

    return system


def state_format_prompt(state: dict) -> str:
    preprompt = ""

    if state["mood"]:
        preprompt += f"""
# Mood
The following moods define how you feel, use them as reference when generating your output:
- {", ".join(state["mood"])}
"""

    for oinfo in state["other_info"]:
        preprompt += f"""
# {oinfo["title"]}
{oinfo["content"]}
"""

    return preprompt+"\n"



def memories_format(memories: list) -> str:
    str_memories = "# Memories\n"
    empty = True

    for memory in memories:
        str_memories+=f"## Memory n.{memory[0]}\n**Title: {memory[1]}**\n**Created at {memory[6]}**\n**Importance: {memory[5]}**\n**Entities: {memory[3]}**\n{memory[4]}\n\n"
        empty = False

    if not empty:
        return str_memories
    return ""


def memories_sentence_to_tags(sentence: str) -> list:
    words = sentence.replace('\n', ' ').split(' ')
    cleaned = [word.strip('.,!?;:~–-+[]()|@#$%^&*`<>').lower() for word in words]

    return cleaned
