import json

def to_json(string: str) -> json.JSONEncoder:
    words = string.split()
    if words[0] == "```json":
        words = words[1:]
        if words[-1] == "```":
            words = words[:-1]

    try:
        result = json.loads(string)

        return result

    except json.JSONDecodeError as e:
        print("\n\x1b[31m\"to_json\": Content not JSON!")
        print(e)
        print("\x1b[0m")

    return json.loads("{}")
