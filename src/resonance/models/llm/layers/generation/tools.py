import os
from ollama import chat
import requests
import base64
import json

from .....apis import keys
from ...prompt_builder import is_correct_llm_data


def generate_openrouter(context: list, model, response_format="") -> str:
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
            "reasoning": {
                # One of the following (not both):
                "effort": "high", # Can be "xhigh", "high", "medium", "low", "minimal" or "none" (OpenAI-style)
                #"max_tokens": 2000, # Specific token limit (Anthropic-style)
                # Optional: Default is false. All models support this.
                "exclude": True, # Set to true to exclude reasoning tokens from response
                # Or enable reasoning with the default parameters:
                "enabled": True# Default: inferred from `effort` or `max_tokens`
            },
            "stream": True
           }

    if response_format:
        payload["response_format"] = response_format


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


def generate_ollama(context: list, model) -> str:
    stream = chat(
        model=model,
        messages=context,
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

def generate_llm_output(context: list, data) -> str:

    if not is_correct_llm_data(data):
        error="""
\x1b[31mERROR ON LLM GENERATION LAYER!
The setting(s) set for generating LLM output is/are incorrect!\x1b[0m
"""

    response_format = ""
    if data.get("response_format"):
        response_format = data.get("response_format")


    match data['provider']:
        case "openrouter":
            ai_output = generate_openrouter(context, data["model"], response_format)
        case "ollama":
            ai_output = generate_ollama(context, data["model"])

        case "":
            error = "\x1b[31mPlease reference a provider!\x1b[0m"
            print(error)
            return error
        case _:
            error = f"\x1b[31mNo such provider \"{data['provider']}\" is available\x1b[0m"
            print(error)
            return error

    return ai_output

def day_summarizer(date: str, name: str):
    filename = f"context/{name}/{date}"

    if os.path.isfile(filename+".sum"):
        print(f"Collecting Day Summary for {date}...")
        try:
            with open(filename+'.sum', 'r') as file:
                return file.read()
        except:
            print("Couldn't read file")
            return None

    context = [{"role":"system", "content":"""
                You will receive a JSON of a conversation
                Your task is to summarize the conversation, keep the important element in your summarization and be detailled with the element that seems important to you, this summary will be used as a memory for the day.
                """}]

    try:
        print(f"Generating Day Summary for {date}...")
        with open(filename+".context", 'r') as file_r:
            content = file_r.read()

        context.append({"role":"user", "content": str(content)})
        ai_response = generate_openrouter(context, "z-ai/glm-5.2")
    
        with open(filename+".sum", 'w') as file_w:
            file_w.write(ai_response)

        return ai_response

    except:
        return None



def remove_state_system_prompt(context: list[dict]):
    
    for i in range(len(context)-1, len(context)-4, -1):
        print("Step")
        print(context[i])
        if context[i].get("role") == "system":
            if i <= 3:
                return
            print("Found!")
            return context.pop(i) 

    return
