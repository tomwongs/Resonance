from ..generation.tools import generate_llm_output 
from ..prompt_builder import is_correct_llm_data

class PerceptionLayer:

    def get_examples(self):
        return [{"role": "system", "content": "Your objective is to interpret the input of a user and classify it through a JSON output. You output ONLY a JSON output nothing else. You need to extract the intent, the emotion and the topic of the input. You don't answer the user, you classify only. Here's the JSON template you should ALWAYS use in your output: { \"intent\": \"\", \"emotion\": \"\", \"topics\": [ \"\", \"\" ]}"}, 
                {"role":"user", "content":"What color is the sky?"}, 
                {"role":"assistant", "content": "{ \"intent\": \"inquiry\", \"emotion\": \"neutral\", \"topics\": [ \"weather\", \"atmosphere\" ]}"},
                {"role": "user", "content": "I feel sad... and alone..."}, 
                {"role": "assistant", "content": "{ \"intent\": \"emotional_support\", \"emotion\": \"sad\", \"topics\": [\"loneliness\"] }"}, 
                {"role": "user", "content": "WHY DO YOU HAVE TO BE LIKE THIS!?"},
                {"role": "user", "content": "{\"intent\": \"conflict_resolution\", \"emotion\": \"anger\", \"topics\": [\"frustration\", \"behavior\"]}"}
            ]
    
    def generate_layer(self, prompt: str, data: dict) -> str:

        if not is_correct_llm_data(data):
            error="""
\x1b[31mERROR ON PERCEPTION LAYER!
The setting(s) set for generating LLM output is/are incorrect!\x1b[0m
"""
    
        context = self.get_examples()
        context.append({"role": "user", "content": prompt})
        llm_output = generate_llm_output(context, data)

        output = f"""
# Perception Layer (Define the intent needed, the emotion of the user and the topic)
If the JSON doesn't contain those informations, disregard it.
{llm_output}
"""
    

        return output + "\n"
