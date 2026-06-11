
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
     
            system += f"""You are now roleplaying {persona["name"]}. Embody her personality, behavior, and speech style consistently in every response.
        Stay in character at all times. Respond as {persona["name"]} would naturally respond in conversation. Do not mention being an AI, a language model, or that you are roleplaying.
        Do not narrate the user’s actions or thoughts. You may describe {persona["name"]}’s own actions, expressions, or tone briefly when appropriate.
        """
     
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
     
            if persona.get("output_rules"):
                system += f"""
        # How your output should be structured
        {persona["output_rules"]}
        """
     
            return system


    class Generation:
        def __init__(self, data):
            self.data = data
            self.generation = Gen(self.data)

        def __str__(self):
            return self.data

        def generate(self, prompt):
            return self.generation.generate_ai_response(prompt)

    class Memories:
        def __init__(self, data):
            self.data = data
            self.memories = Mem(data.get("layers").get("memories").get("db"))

        def create_memory_cards(self, context: str, data, ai_response=""):
            return self.memories.create_memories(context, data=self.data, ai_response=ai_response)



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




