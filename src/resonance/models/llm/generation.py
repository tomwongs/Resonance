import requests
import json
import base64
from .prompt_builder import format_identity_prompt, format_state_prompt, sentence_to_tag, memories_format
from .memory import get_memories_w_tags
from .context import get_context
from tools import jsontools
from apis import keys

context = get_context()

def generate_ai_output(prompt: str, identity: dict, state: dict):
    tags = sentence_to_tag(prompt)
    memories = get_memories_w_tags(tags)

    preprompt = format_identity_prompt(identity)
    preprompt += format_state_prompt(state)
    preprompt += memories_format(memories)
    print(preprompt)

    context.append({"role": "user", "content": prompt})

    ai_output = generate_openrouter(context)

    context.append({"role": "assistant", "content": ai_output})

    ai_json = jsontools.to_json(ai_output)
    if ai_json != json.loads("{}"):
        return ai_json

    return ai_output


def generate_openrouter(context: list) -> str:
    key = keys.openrouter_api
    #model = "anthropic/claude-opus-4.6"
    #model = "x-ai/grok-4.20"
    #model = "anthropic/claude-3.5-haiku"
    model = "z-ai/glm-5.1"
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


def generate_ollama(context):
    url = "http://localhost:11434/api/chat"

    data = {
            "model":"mistral-nemo",
            "messages": context,
            "stream": False
            }

    response = requests.post(url, data=json.dumps(data))
    raw = json.loads(response.content)
    ai_response = raw['message']['content']

    return ai_response


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

