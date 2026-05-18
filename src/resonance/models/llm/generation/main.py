import json
from .tools import generate_llm_output
from ..layers.perception import PerceptionLayer
from ..prompt_builder import persona_format_prompt, state_format_prompt, memories_sentence_to_tags, memories_format, output_format_prompt, is_correct_llm_data
from ..layers.memories.main import Memories
from ....tools import jsontools


class Generation:

    def generate_ai_response(self, context: list, data: dict):

        preprompt = ""
        prompt = context[-1]["content"]

        if layers := data.get("layers"):

            for layer in layers:

    
                if identity_data := layer.get("identity"):
                    preprompt += persona_format_prompt(identity_data["persona"])
                    preprompt += state_format_prompt(identity_data["state"])

    
                if perception_data := layer.get("perception"):
                    if not is_correct_llm_data(perception_data):
                        error = "\x1b[31mIncorrect data for Perception Layer!\x1b[0m"
                        print(error)
                        return error

                    PLayer = PerceptionLayer()
                    preprompt += PLayer.generate_layer(prompt, perception_data)

    
                if layer.get("memories"):
                    MLayer = Memories()
                    tags = memories_sentence_to_tags(prompt)
                    memories = MLayer.get_memories_w_tags(tags)
                    preprompt += memories_format(memories)

    
                if layer.get("thoughts"):
                    preprompt += output_format_prompt({"thoughts": "Your current thoughts, embracing your personality and state, without line breaks.", "thinking_process": "How you plan on reacting based on your personality, your state and your data. Without line breaks", "decisions": "The decisions you're taking and reflecting in your output. Without line breaks", "output": "Message you want to output.\nWith multiple lines if needed."})

    
        baked_prompt = preprompt + "\n" + prompt
        context.append({"role": "user", "content": baked_prompt})
        print(baked_prompt)

        ai_output = generate_llm_output(context, data)

        context.append({"role": "assistant", "content": ai_output})

        ai_json = jsontools.to_json(ai_output)
        if ai_json != json.loads("{}"):
            return ai_json

        return ai_output
