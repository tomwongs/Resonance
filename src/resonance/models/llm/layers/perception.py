from ..generation import generate_llm_output, correct_llm_settings

def get_examples():
    return [{"role": "system", "content": "You are an AI made to interpret the input of a user and classify it through a JSON output. You output ONLY a JSON output nothing else. You need to extract the intent, the emotion and the topic of the input."}, 
            {"role":"user", "content":"What color is the sky?"}, 
            {"role":"assistant", "content": "{ \"intent\": \"inquiry\", \"emotion\": \"neutral\", \"topics\": [ \"weather\", \"atmosphere\" ]}"},
            {"role": "user", "content": "I feel sad... and alone..."}, 
            {"role": "assistant", "content": "{ \"intent\": \"emotional_support\", \"emotion\": \"sad\", \"topics\": [\"loneliness\"] }"}, 
            {"role": "user", "content": "WHY DO YOU HAVE TO BE LIKE THIS!?"},
            {"role": "user", "content": "{\"intent\": \"conflict_resolution\", \"emotion\": \"anger\", \"topics\": [\"frustration\", \"behavior\"]}"}
            ]

def generate_perception_layer(prompt: str, settings: dict) -> str:

    if not correct_llm_settings(settings):
        error="""
        \x1b[31mERROR ON PERCEPTION LAYER!
        The setting(s) set for generating LLM output is/are incorrect!\x1b[0m
        """

    context = get_examples()
    context.append({"role": "user", "content": prompt})
    llm_output = generate_llm_output(context, settings)


    return llm_output
