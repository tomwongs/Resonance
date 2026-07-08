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
