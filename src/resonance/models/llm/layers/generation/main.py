import json
from typing import Any

from .tools import generate_llm_output, remove_state_system_prompt
from ...context.main import get_context
from ...prompt_builder import persona_format_prompt
from .....tools import jsontools, date 


class Generation:

    def __init__(self, ai: dict, data: dict[str, Any]):
        self.context = get_context(data, date.date_time("date"))
        self.ai = ai
        self.data = data
        self.context_file = f"context/{data['layers']['identity']['persona']['name']}/{date.date_time('date')}.context"

    def generate_ai_response(self, prompt: str) -> dict[str, Any]:

        print('-'*10)
        print(prompt)
        print('-'*10)

        system = ""
        ai_output = ""
        retries = 6
        
        if layers := self.data.get("layers"):
            if identity_data := layers.get("identity"):
                system += self.ai["identity"].state_format_prompt(identity_data["state"])
         
             
            #if perception_data := layers.get("perception"):
            #    if not is_correct_llm_data(perception_data):
            #        error = "\x1b[31mIncorrect data for Perception Layer!\x1b[0m"
            #        print(error)
            #        return {"error":error}
            # 
            #    preprompt += PLayer.generate_layer(prompt, perception_data)
         
             
            if layers.get("memories"):
                tags = self.ai["memories"].memories_sentence_to_tags(prompt)
                memories = self.ai["memories"].get_memories_w_tags(tags)
                system += self.ai["memories"].memories_format(memories)

            system += "\n"

            remove_state_system_prompt(self.context)
            self.context.append({"role": "system", "content": system})

        self.context.append({"role": "user", "content": prompt})

        while ai_output == "" and retries != 0:
            print("Generating output...")
            ai_output = generate_llm_output(self.context, self.data)
            retries-=1

        ai_json = jsontools.to_json(ai_output)

        self.context.append({"role": "assistant", "content": str(ai_json)})

        with open(self.context_file, 'w') as file:
            file.write(json.dumps(self.context))

        return ai_json

    def update_system_prompt(self):
        self.context[0] = persona_format_prompt(self.data.get("layers").get("identity").get("persona"))
        with open(self.context_file, 'w') as file:
            file.write(json.dumps(self.context))
        return
        
