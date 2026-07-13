import json
from typing import Any

from .tools import generate_llm_output, remove_state_system_prompt
from ...context.main import get_context
from .....tools import jsontools, date 


class Generation:

    def __init__(self, ai: dict, data: dict[str, Any]):
        self.context = get_context(ai, data, date.date_time("date"))
        self.ai = ai
        self.data = data
        self.context_file = f"context/{data['layers']['identity']['persona']['name']}/{date.date_time('date')}.context"

    def generate_ai_response(self, prompt: str, images=[]) -> dict[str, Any]:
        print('\n------- PROMPT ------')
        print(prompt)
        print('-'*20)

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

        while ai_output == "" and retries > 1:
            print("Generating output...")
            ai_output = generate_llm_output(context=self.context, images=images, data=self.data)
            retries-=1

        ai_json = json.loads(ai_output)

        self.context.append({"role": "assistant", "content": ai_output})

        with open(self.context_file, 'w') as file:
            file.write(json.dumps(self.context))

        return ai_json

    def update_system_prompt(self):
        name = self.data['layers']['identity']['persona']['name']
        self.context[0] = {"role": "system", "content": self.ai["identity"].persona_format_prompt(self.data.get("layers").get("identity").get("persona"))}
        if output_rules := self.data['output_rules']:
            self.context[1] = {"role": "system", "content": output_rules}
            self.context[2] = {"role": "system", "content": f"""You are now roleplaying {name}. Embody her personality, behavior, and speech style consistently in every response. Stay in character at all times. Respond as {name} would naturally respond in conversation. Do not mention being an AI, a language model, or that you are roleplaying. Do not narrate the user’s actions or thoughts. You may describe {name}’s own actions, expressions, or tone briefly when appropriate."""}
        else:
            self.context[1] = {"role": "system", "content": f"""You are now roleplaying {name}. Embody her personality, behavior, and speech style consistently in every response. Stay in character at all times. Respond as {name} would naturally respond in conversation. Do not mention being an AI, a language model, or that you are roleplaying. Do not narrate the user’s actions or thoughts. You may describe {name}’s own actions, expressions, or tone briefly when appropriate."""}

        with open(self.context_file, 'w') as file:
            file.write(json.dumps(self.context))
        return
        
