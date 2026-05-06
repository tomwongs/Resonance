import ollama
import requests
import json
import base64
from .prompt_builder import identity_format_prompt, state_format_prompt, memories_sentence_to_tags, memories_format
from .memory import get_memories_w_tags
from .context import get_context
from ...tools import jsontools
from ...apis import keys

context = get_context()
openrouter_model = "z-ai/glm-5.1"
ollama_model = "mistral-nemo"

def correct_llm_settings(settings={"provider":"", "model":""}):
    if not settings.get("provider"):
        error = "\x1b[31mMissing a provider.\x1b[0m"
        print(error)
        return False

    if not settings.get("model"):
        error = "\x1b[31mMissing a model.\x1b[0m"
        print(error)
        return False

    return True


def generate_llm_output(context: list, settings={"provider":"", "model":""}) -> str:

    if not correct_llm_settings(settings):
        error="""
        \x1b[31mERROR ON LLM GENERATION LAYER!
        The setting(s) set for generating LLM output is/are incorrect!\x1b[0m
        """


    match settings['provider']:
        case "openrouter":
            ai_output = generate_openrouter(context, openrouter_model)
        case "ollama":
            ai_output = generate_ollama(context, ollama_model)

        case "":
            error = "\x1b[31mPlease reference a provider!\x1b[0m"
            print(error)
            return error
        case _:
            error = f"\x1b[31mNo such provider \"{settings['provider']}\" is available\x1b[0m"
            print(error)
            return error

    return ai_output
            



def generate_ai_response(prompt: str, identity: dict, state: dict, settings={"provider": "", "model": ""}):
    tags = memories_sentence_to_tags(prompt)
    memories = get_memories_w_tags(tags)

    preprompt = identity_format_prompt(identity)
    preprompt += state_format_prompt(state)
    preprompt += memories_format(memories)
    print(preprompt)

    context.append({"role": "user", "content": prompt})

    if layers := settings.get("layers"):
        for layer in layers:
#            match layer.get("perception"):
            pass

    ai_output = generate_llm_output(context, settings)

    context.append({"role": "assistant", "content": ai_output})

    ai_json = jsontools.to_json(ai_output)
    if ai_json != json.loads("{}"):
        return ai_json

    return ai_output


def generate_openrouter(context: list, model) -> str:
    key = keys.openrouter_api
    #model = "anthropic/claude-opus-4.6"
    #model = "x-ai/grok-4.20"
    #model = "anthropic/claude-3.5-haiku"
    #model = "z-ai/glm-5.1"
    #model = "z-ai/glm-4.6"
    url = 'https://openrouter.ai/api/v1/chat/completions'

    headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
            }

    payload = {
            "model": model,
            "messages": context,
            "stream": True
           }


    response = requests.post(
        url,
        headers=headers,
        json=payload,
        stream=True
    )

    result = ""
    # Check initial HTTP status for pre-stream errors
    if response.status_code != 200:
        error_data = response.json()
        print(f"Error: {error_data['error']['message']}")
        return ""

    # Process stream and handle mid-stream errors
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith('data: '):
                data = line_text[6:]
                if data == '[DONE]':
                    break
                try:
                    parsed = json.loads(data)
                    # Check for mid-stream error
                    if 'error' in parsed:
                        print(f"Stream error: {parsed['error']['message']}")
                        # Check finish_reason if needed
                        if parsed.get('choices', [{}])[0].get('finish_reason') == 'error':
                            print("Stream terminated due to error")
                        break
                    # Process normal content
                    content = parsed['choices'][0]['delta'].get('content')
                    if content:
                        result+=content
                        print(content, end='', flush=True)
                except json.JSONDecodeError:
                    pass

    return result 


def generate_ollama(context, model):
    stream = chat(
        model='llama3.1:8b',
        messages=[{'role': 'user', 'content': 'What is 17 × 23?'}],
        stream=True,
    )

    in_thinking = False
    content = ''
    thinking = ''
    for chunk in stream:
        if chunk.message.thinking:
            if not in_thinking:
                in_thinking = True
                print('Thinking:\n', end='', flush=True)
            print(chunk.message.thinking, end='', flush=True)
            # accumulate the partial thinking 
            thinking += chunk.message.thinking
        elif chunk.message.content:
            if in_thinking:
                in_thinking = False
                print('\n\nAnswer:\n', end='', flush=True)
            print(chunk.message.content, end='', flush=True)
            # accumulate the partial content
            content += chunk.message.content

        # append the accumulated fields to the messages for the next request
        new_messages = [{ 'role': 'assistant', 'thinking': thinking, 'content': content }]

    return content


def encode_image(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    b64 = base64.b64encode(response.content).decode("utf-8")
    print(response.content)
    return b64


def send_to_llava(image_url: str):
    key = keys.openrouter_api
    model = "qwen/qwen3-vl-8b-instruct"
    url = 'https://openrouter.ai/api/v1/chat/completions'
    prompt = """Describe the image with as much details as possible, your output are gonna be fed into another AI.
    If there are people describe them as best as possible.
    Analyze the image and respond ONLY in JSON:
        {{
            "scene": "...",
            "objects": ["..."],
            "actions": ["..."],
            "important_elements": ["..."],
            "description": ""
        }}
    """

    headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
            }

    data = {
            "model": model,
            "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ]
           }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    raw = json.loads(response.content)
    try:
        ai_response = raw['choices'][0]['message']['content']
    except Exception as e:
        print(raw)
        print(e)
        ai_response = ""
    return ai_response


def get_memories() -> list:
    return []
