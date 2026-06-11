import json
from typing import Any

from .tools import generate_llm_output
from ...context.main import get_context
from .....tools import jsontools, date


class Generation:

    def __init__(self, data: dict[str, Any]):
        self.context = get_context(data, date.date_time("date"))
        self.data = data
        self.context_file = f"context/{data['layers']['identity']['persona']['name']}/{date.date_time('date')}.context"

    def generate_ai_response(self, prompt: str) -> dict[str, Any]:

        print('-'*10)
        print(prompt)
        print('-'*10)
        self.context.append({"role": "user", "content": prompt})

        ai_output = generate_llm_output(self.context, self.data)

        ai_json = jsontools.to_json(ai_output)

        self.context.append({"role": "assistant", "content": str(ai_json)})

        with open(self.context_file, 'w') as file:
            file.write(json.dumps(self.context))

        return ai_json
