from typing import Any

from .models.llm.layers.main import Layers


class Resonance:

    class AI:

        def __init__(self, data: dict):
            self.data = data
            self.ai = {"identity": Layers.Identity(data), "llm": Layers.Generation(data), "memories": Layers.Memories("memories.db")}


        def generate(self, prompt: str):
            preprompt = self.generate_layers_preprompt(prompt)
            nprompt = preprompt + prompt
            return self.ai["llm"].generate(nprompt)


        def create_memories(self, day_context: str, ai_response=""):
            return self.ai["memories"].create_memories(day_context, self.data, ai_response)

        #def fetch_memories(self, )
            

        def generate_layers_preprompt(self, prompt: str) -> str:

            preprompt = ""
            if layers := self.data.get("layers"):
                if identity_data := layers.get("identity"):
                    preprompt += self.ai["identity"].state_format_prompt(identity_data["state"])
         
             
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
                    preprompt += self.ai["memories"].memories_format(memories)

                preprompt += "\n"

            return preprompt
