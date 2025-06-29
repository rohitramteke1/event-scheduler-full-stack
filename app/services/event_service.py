from app.models.event_model import Event
from app.services.dynamodb_service import DynamoDBService
from datetime import datetime

# Initialize DynamoDB service
db_service = DynamoDBService()

# Initialize table on startup
try:
    db_service.create_table_if_not_exists()
except Exception as e:
    print(f"⚠️ Warning: Could not initialize DynamoDB table: {e}")

# Get all events sorted by start_time
def get_all_events():
    events = db_service.get_all_events()
    return events

# Create a new event
def create_event(data):
    required_fields = ["title", "description", "start_time", "end_time"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"{field} is required")

    # optional
    recurrence = data.get("recurrence") 
    email = data.get("email") 

    new_event = Event(
        title=data["title"],
        description=data["description"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        recurrence=recurrence,
        email=email
    )

    # Save to DynamoDB
    event_dict = new_event.to_dict()
    saved_event = db_service.create_event(event_dict)
    return saved_event

# Update an existing event
def update_event(event_id, data, partial=False):
    if partial:
        # For partial updates, get existing event and merge
        existing_event = db_service.get_event_by_id(event_id)
        if not existing_event:
            raise ValueError("Event not found")
        
        # Update only provided fields
        for key, value in data.items():
            if value is not None:
                existing_event[key] = value
        
        updated_event = db_service.update_event(event_id, existing_event)
    else:
        # For full updates, validate required fields
        required_fields = ["title", "description", "start_time", "end_time"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"{field} is required")
        
        updated_event = db_service.update_event(event_id, data)
    
    return updated_event

# Delete an event
def delete_event(event_id):
    return db_service.delete_event(event_id)

# Get a single event by ID
def get_event_by_id(event_id):
    return db_service.get_event_by_id(event_id)

def search_event(query):
    return db_service.search_events(query)