# ai/scheduler_ai.py
import requests, os, json
from datetime import datetime, timedelta

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
MODEL_NAME  = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')

def chat(prompt, system='You are a helpful assistant'):
    url  = f'{OLLAMA_HOST}/api/generate'
    body = {
        'model': MODEL_NAME,
        'prompt': f'{system}\n\n{prompt}',
        'stream': False        # easier for simple use‑cases
    }
    try:
        r = requests.post(url, json=body, timeout=120)
        r.raise_for_status()
        return r.json()['response'].strip()
    except Exception as e:
        print(f"Warning: AI service not available: {e}")
        return "AI service unavailable"

def parse_event(user_input: str) -> dict:
    """Parse natural language input into event details"""
    system_prompt = """You are an AI assistant that parses natural language event descriptions into structured data.
    Return a JSON object with the following fields:
    - summary: The event title
    - start: ISO datetime string
    - end: ISO datetime string
    - timezone: timezone (default to 'UTC')
    
    If times are not specified, assume 1 hour duration and reasonable business hours."""
    
    try:
        response = chat(user_input, system_prompt)
        # Try to parse as JSON, fallback to basic structure if parsing fails
        try:
            return json.loads(response)
        except:
            # Fallback structure
            return {
                'summary': user_input[:50] + "..." if len(user_input) > 50 else user_input,
                'start': (datetime.now() + timedelta(days=1)).isoformat(),
                'end': (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
                'timezone': 'UTC'
            }
    except Exception as e:
        print(f"Error parsing event: {e}")
        return {
            'summary': user_input[:50] + "..." if len(user_input) > 50 else user_input,
            'start': (datetime.now() + timedelta(days=1)).isoformat(),
            'end': (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            'timezone': 'UTC'
        }

def schedule_event(natural_text: str, existing_events: list, create_event_func) -> dict:
    """Main function to schedule an event from natural language input"""
    try:
        # Parse the natural language input
        event_data = parse_event(natural_text)
        
        # Create the event using the provided function
        created_event = create_event_func(event_data)
        
        # Generate meeting preparation notes
        prep_notes = f"Meeting preparation for: {event_data.get('summary', 'Event')}"
        
        return {
            'event': created_event,
            'prep_notes': prep_notes
        }
    except Exception as e:
        print(f"Error scheduling event: {e}")
        return {
            'event': {'id': 'error', 'summary': 'Error creating event'},
            'prep_notes': 'Error occurred while scheduling event'
        }

# quick sanity check
if __name__ == '__main__':
    print(chat('Parse this: “Interview with Alice next Monday at 9 AM for 45 minutes.”'))
