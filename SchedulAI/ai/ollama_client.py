import os
import requests

# Host and model configuration (env‑configurable)
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
MODEL_NAME  = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')


def chat(prompt: str, system: str = 'You are a helpful assistant') -> str:
    """
    Send a prompt to the local Ollama LLM and return the text response.
    """
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        'model': MODEL_NAME,
        'prompt': f"{system}\n\n{prompt}",
        'stream': False,
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get('response', '').strip()


# Quick smoke‑test when run directly
if __name__ == '__main__':
    test = 'Parse this: "Interview with Alice next Monday at 9 AM for 45 minutes."'
    print(chat(test))