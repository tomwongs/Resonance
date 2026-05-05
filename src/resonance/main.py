import memory as aimem

import json

#context = [{"role":"user", "content": "What color is the sky?"}]
#print("OUTPUT:", aigen.generate_openrouter(context))

context = open("context-2026-04-17.sum", 'r').read()
ai_response = open("output.txt", 'r').read()

print(aimem.create_memories(context, ai_response))
