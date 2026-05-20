import json
from typing import Any

from .tools import generate_llm_output, date_time
from ...context.main import get_context
from ..perception.main import PerceptionLayer
from ...prompt_builder import state_format_prompt, memories_sentence_to_tags, memories_format, is_correct_llm_data
from ..memories.main import Memories
from .....tools import jsontools


class Generation:

    def __init__(self, data: dict[str, Any]):
        self.context = get_context(data, date_time("date"))
        self.data = data
        self.context_file = f"context/{data['layers']['identity']['persona']['name']}/{date_time('date')}.context"

    def generate_ai_response(self, prompt: str) -> dict[str, Any]:

        preprompt = ""

        if layers := self.data.get("layers"):

            if identity_data := layers.get("identity"):
                preprompt += state_format_prompt(identity_data["state"])

    
            if perception_data := layers.get("perception"):
                if not is_correct_llm_data(perception_data):
                    error = "\x1b[31mIncorrect data for Perception Layer!\x1b[0m"
                    print(error)
                    return {"error":error}

                PLayer = PerceptionLayer()
                preprompt += PLayer.generate_layer(prompt, perception_data)

    
            if layers.get("memories"):
                MLayer = Memories()
                tags = memories_sentence_to_tags(prompt)
                memories = MLayer.get_memories_w_tags(tags)
                preprompt += memories_format(memories)

    
        baked_prompt = preprompt + "\n" + prompt

        print(preprompt)

        self.context.append({"role": "user", "content": baked_prompt})

        ai_output = generate_llm_output(self.context, self.data)

        ai_json = jsontools.to_json(ai_output)

        self.context.append({"role": "assistant", "content": str(ai_json)})


        with open(self.context_file, 'w') as file:
            file.write(json.dumps(self.context))

        return ai_json
