
from .generation.main import Generation as Gen
from .memories.main import Memories as Mem
from .perception.main import PerceptionLayer

class Layers:


    def __init__(self, data):
        self.data = data


    class Identity:

        def __init__(self, data: dict):
            self.data = data
    
    
        def persona_format_prompt(self, persona: dict) -> str:
            system = ""
     
            if not persona["name"] or not persona["personality"]:
                print("\x1b[31mPlease provide a Name and a Personality for the AI.\x1b[0m")
                return ""
     
            system += f"""
# {persona["name"].title()}'s description 
{persona["description"]}
     
# {persona["name"].title()}'s personality
{persona["personality"]}
"""
         
            if persona.get("traits"):
                system += f"""
# {persona["name"].title()}'s personality traits
- {", ".join(persona['traits'])}
"""
     
            if persona.get("speech_style"):
                system += f"""
# {persona["name"].title()}'s speech style
- {persona['speech_style']}
"""
     
            if persona.get("values"):
                system += f"""
# {persona["name"].title()}'s core values
- {", ".join(persona['values'])}
"""
     
            if persona.get("rules"):
                system += f"""
# You must follow these rules:
- {", ".join(persona['rules'])}
"""
     
            if other_info := persona.get("other_info"):
                for oinfo in other_info:
                    system += f"""
# {oinfo["title"]}
{oinfo["content"]}
"""
            return system


        def state_format_prompt(self, state={}) -> str:
            preprompt = ""
     
            if state.get("mood"):
                preprompt += f"""
# Mood
The following moods define how you feel, use them as reference when generating your output:
- {", ".join(state["mood"])}
"""
     
            for info in state.get("info"):
                if callable(info["title"]):
                    preprompt += f"\n{info['title']()}"
                else:
                    preprompt += f"\n{info['title']}"
                if callable(info["content"]):
                    preprompt += f"\n{info['content']()}\n"
                else:
                    preprompt += f"\n{info['content']}"
    
            return preprompt+"\n"


    class Generation:
        def __init__(self, ai, data):
            self.ai = ai
            self.data = data
            self.generation = Gen(ai, self.data)

        def __str__(self):
            return self.data

        def generate(self, prompt, images=[]):
            return self.generation.generate_ai_response(prompt, images)


        def update_system_prompt(self):
            return self.generation.update_system_prompt()

    class Memories:
        def __init__(self, data):
            self.data = data
            self.memories = Mem(data)

        def create_memory_cards(self, context: str, data={}, ai_response=""):
            return self.memories.create_memories(context, data=self.data, ai_response=ai_response)


        def get_memories_w_tags(self, tags: list):
            return self.memories.get_memories_w_tags(tags)


        def get_memories_w_date(self, date: str, date_type=0) -> list:
            return self.get_memories_w_date(date, date_type)


        def memories_format(self, memories: list) -> str:
            str_memories = "# Memories\n"
            empty = True
     
            for memory in memories:
                str_memories+=f"## Memory n.{memory[0]}\n**Title: {memory[1]}**\n**Created at {memory[6]}**\n**Importance: {memory[5]}**\n**Entities: {memory[3]}**\n{memory[4]}\n\n"
                empty = False
    
            if not empty:
                return str_memories
            return ""


        def memories_sentence_to_tags(self, sentence: str) -> list:
            words = sentence.replace('\n', ' ').split(' ')
            cleaned = [word.strip('.,!?;:~–-+[]()|@#$%^&*`<>').lower() for word in words]
     
            return cleaned
