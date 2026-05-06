def identity_format_prompt(identity: dict) -> str:
    system = ""

    if not identity["name"] or not identity["personality"]:
        print("\x1b[31mPlease provide a Name and a Personality for the AI.\x1b[0m")
        return ""

    system += f"""
# Your Identity
You are {identity["name"]}
{identity["description"]}

# Personality
{identity["personality"]}
"""
    
    if identity.get("traits"):
        system += f"""
# Personality Traits
- {", ".join(identity['traits'])}
"""

    if identity.get("speech_style"):
        system += f"""
# Speech style
- {identity['speech_style']}
"""

    if identity.get("values"):
        system += f"""
# Core Values
- {", ".join(identity['values'])}
"""

    if identity.get("rules"):
        system += f"""
# You must follow these rules:
- {", ".join(identity['rules'])}
"""

    if other_info := identity.get("other_info"):
        for oinfo in other_info:
            system += f"""
# {oinfo["title"]}
{oinfo["content"]}
"""

    if identity.get("output_rules"):
        system += f"""
# Output Rules
{identity["output_rules"]}
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
