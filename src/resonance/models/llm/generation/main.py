import json
from .tools import generate_llm_output
from ..layers.perception import generate_layer as perception_generate_layer
from ..prompt_builder import persona_format_prompt, state_format_prompt, memories_sentence_to_tags, memories_format, output_format_prompt, is_correct_llm_data
from ..memory import get_memories_w_tags
from ..context.main import get_context
from ....tools import jsontools

context = get_context()


def generate_ai_response(prompt: str, data: dict):

    preprompt = ""

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

                preprompt += perception_generate_layer(prompt, perception_data)


            if layer.get("memories"):
                tags = memories_sentence_to_tags(prompt)
                memories = get_memories_w_tags(tags)
                preprompt += memories_format(memories)


            if layer.get("thoughts"):
                preprompt += output_format_prompt({"thoughts": "Your current thoughts, without line breaks.", "thinking_process": "How you plan on reacting based on all the data you've been given.", "decisions": "A plan of what to do and respond.\n1. Beginning.\n2. Next step...\n3. Finally.", "output": "Message you want to output.\nWith multiple lines."})


    baked_prompt = preprompt + "\n" + prompt
    context.append({"role": "user", "content": baked_prompt})
    print(baked_prompt)

    ai_output = generate_llm_output(context, data)

    context.append({"role": "assistant", "content": ai_output})

    ai_json = jsontools.to_json(ai_output)
    if ai_json != json.loads("{}"):
        return ai_json

    return ai_output




def get_memories() -> list:
    return []
