import json
import os
from app.models.event_model import Event
from app.config import EVENT_FILE_PATH

def load_events():
    if not os.path.exists(EVENT_FILE_PATH):
        return []

    with open(EVENT_FILE_PATH, "r") as f:
        try:
            data = json.load(f)
            return [Event.from_dict(item) for item in data]
        except json.JSONDecodeError:
            return []

def save_events(events):
    with open(EVENT_FILE_PATH, "w") as f:
        json.dump([event.to_dict() for event in events], f, indent=4)
