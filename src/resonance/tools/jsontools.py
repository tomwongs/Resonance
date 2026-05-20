from typing import Any
import ast
import json

def to_json(string: str) -> dict[str, Any]:
    words = string.split()

    if words and words[0] == "```json":
        words = words[1:]

        if words and words[-1] == "```":
            words = words[:-1]

        string = " ".join(words)

    try:
        result = ast.literal_eval(string)
        return result


    except Exception as e:
        print("\x1b[31m",e,"\x1b[0m")
        return {"output": string}
