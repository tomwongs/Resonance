import os
from ollama import chat
import requests
import base64
import json

from .....apis import keys
from ...prompt_builder import is_correct_llm_data

key = keys.openrouter_api

def get_model_info(model_id: str):
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {key}"}
    )
    response.raise_for_status()

    models = response.json()["data"]
    return next((m for m in models if m["id"] == model_id), None)


def model_supports_images(model_id: str) -> bool:
    info = get_model_info(model_id)
    if info is None:
        return False

    return "image" in info.get("architecture", {}).get("input_modalities", [])



def generate_openrouter(context: list, images=[], model="deepseek/deepseek-v3.2", response_format="") -> str:
    url = 'https://openrouter.ai/api/v1/chat/completions'

    headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
            }

    if images:
        if model_supports_images(model):
            context[-1]["content"] = [
                {
                    "type": "text",
                    "text": context[-1]["content"]
                }
            ]

            for image_url in images:
                image_format = {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }

                context[-1]["content"].append(image_format)

        else:
            print("Doesn't support image visualization! Reading through another AI...")
            images_prompt = ""
            count = 1
            for image in images:
                print(image)
                images_prompt += f"Image {count}:\n{send_to_llava(image)}\n\n"
                count+=1

            print("Images Description\n",images_prompt)

            context[-1]["content"] = context[-1]["content"] + "\n\n" + images_prompt

            

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

    print()

    return result 


# HAVEN'T BEEN UPDATED IN A WHILE, DISREGARD.
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
    model = "openai/gpt-4.1"
    #model = "qwen/qwen3-vl-8b-instruct"
    url = 'https://openrouter.ai/api/v1/chat/completions'
    prompt = """Describe the image with as much details as possible, your output are gonna be fed into another AI.
If there are people describe them as best as possible.
If there are known personalities, characters, write their names directly with where they are referenced in.
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

def generate_llm_output(context: list, data, images=[]) -> str:

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
            ai_output = generate_openrouter(context, images, data["model"], response_format)
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
        if context[i].get("role") == "system":
            if i <= 3:
                return
            return context.pop(i) 

    return
