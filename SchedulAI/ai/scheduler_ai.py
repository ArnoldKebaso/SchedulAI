# ai/ollama_client.py
import requests, os, json

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
MODEL_NAME  = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')

def chat(prompt, system='You are a helpful assistant'):
    url  = f'{OLLAMA_HOST}/api/generate'
    body = {
        'model': MODEL_NAME,
        'prompt': f'{system}\n\n{prompt}',
        'stream': False        # easier for simple use‑cases
    }
    r = requests.post(url, json=body, timeout=120)
    r.raise_for_status()
    return r.json()['response'].strip()

# quick sanity check
if __name__ == '__main__':
    print(chat('Parse this: “Interview with Alice next Monday at 9 AM for 45 minutes.”'))
