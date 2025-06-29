import uuid
from datetime import datetime

class Event:
    def __init__(self, title, description, start_time, end_time, recurrence=None, email=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.recurrence = recurrence  # 'daily', 'weekly', 'monthly', or None
        self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "recurrence": self.recurrence,
            "email": self.email
        }

    @staticmethod
    def from_dict(data):
        return Event(
            title=data["title"],
            description=data["description"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            recurrence=data.get("recurrence"),
            email=data.get("email"), 
            id=data.get("id")
        )

    def __repr__(self):
        return f"<Event {self.title} from {self.start_time} to {self.end_time}>"
