from typing import Any

from .models.llm.layers.main import Layers


class Resonance:

    class AI:

        def __init__(self, data: dict):
            self.data = data
            self.identity = Layers.Identity(data)
            self.memories = Layers.Memories(data)
            self.generation = Layers.Generation({"identity": self.identity, "memories": self.memories}, data)
            self.ai = {"identity": self.identity, "llm": self.generation, "memories": self.memories}


        def generate(self, prompt: str):
            return self.ai["llm"].generate(prompt)


        def create_memories(self, day_context: str, ai_response=""):
            return self.ai["memories"].create_memories(day_context, self.data, ai_response)


        def update_system_prompt(self):
            return self.generation.update_system_prompt()
