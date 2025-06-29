import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

class EventAPIClient:
    """Client for communicating with the Event Scheduler Flask API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/events"
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to the API"""
        url = f"{self.api_base}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Cannot connect to the API server. Make sure the Flask app is running.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError("Event not found")
            elif e.response.status_code == 400:
                error_data = e.response.json()
                raise ValueError(error_data.get('error', 'Bad request'))
            else:
                raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_all_events(self) -> List[Dict]:
        """Get all events"""
        return self._make_request("GET", "/")
    
    def create_event(self, event_data: Dict) -> Dict:
        """Create a new event"""
        return self._make_request("POST", "/", event_data)
    
    def update_event(self, event_id: str, event_data: Dict, partial: bool = False) -> Dict:
        """Update an existing event"""
        method = "PATCH" if partial else "PUT"
        return self._make_request(method, f"/{event_id}", event_data)
    
    def delete_event(self, event_id: str) -> Dict:
        """Delete an event"""
        return self._make_request("DELETE", f"/{event_id}")
    
    def search_events(self, query: str) -> List[Dict]:
        """Search events by title or description"""
        return self._make_request("GET", f"/search?q={query}")
    
    def get_upcoming_events(self, hours: int = 24) -> List[Dict]:
        """Get events happening in the next N hours"""
        all_events = self.get_all_events()
        now = datetime.now()
        upcoming = []
        
        for event in all_events:
            try:
                start_time = datetime.fromisoformat(event['start_time'])
                if start_time >= now and start_time <= now.replace(hour=now.hour + hours):
                    upcoming.append(event)
            except (ValueError, TypeError):
                continue
        
        return sorted(upcoming, key=lambda x: x['start_time'])
    
    def get_today_events(self) -> List[Dict]:
        """Get events happening today"""
        all_events = self.get_all_events()
        today = datetime.now().date()
        today_events = []
        
        for event in all_events:
            try:
                start_time = datetime.fromisoformat(event['start_time'])
                if start_time.date() == today:
                    today_events.append(event)
            except (ValueError, TypeError):
                continue
        
        return sorted(today_events, key=lambda x: x['start_time'])
    
    def get_event_by_id(self, event_id: str) -> Dict:
        """Get a single event by its ID"""
        return self._make_request("GET", f"/{event_id}") 