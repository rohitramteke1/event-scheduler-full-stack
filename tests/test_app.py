import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app import create_app
from app.models.event_model import Event
from app.services.event_service import (
    get_all_events,
    create_event,
    update_event,
    delete_event,
    search_event
)


class TestEventSchedulerApp:
    """Test suite for Event Scheduler Flask Application"""

    @pytest.fixture
    def app(self):
        """Create and configure a new app instance for each test."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client for the Flask application."""
        return app.test_client()

    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing."""
        return {
            "title": "Test Meeting",
            "description": "A test meeting for unit testing",
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T11:00:00",
            "recurrence": "daily",
            "email": "test@example.com"
        }

    @pytest.fixture
    def sample_event(self, sample_event_data):
        """Create a sample Event object."""
        return Event(
            title=sample_event_data["title"],
            description=sample_event_data["description"],
            start_time=sample_event_data["start_time"],
            end_time=sample_event_data["end_time"],
            recurrence=sample_event_data["recurrence"],
            email=sample_event_data["email"]
        )

    def test_app_creation(self, app):
        """Test that the Flask app is created successfully."""
        assert app is not None
        assert app.config['TESTING'] is True

    def test_home_route_not_found(self, client):
        """Test that home route returns 404 (since we only have /api/events routes)."""
        response = client.get('/')
        assert response.status_code == 404

    def test_events_list_empty(self, client):
        """Test getting all events when none exist."""
        with patch('app.services.dynamodb_service.DynamoDBService.get_all_events', return_value=[]):
            response = client.get('/api/events/')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []

    def test_events_list_with_data(self, client, sample_event):
        """Test getting all events when events exist."""
        with patch('app.services.dynamodb_service.DynamoDBService.get_all_events', return_value=[sample_event.to_dict()]):
            response = client.get('/api/events/')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['title'] == sample_event.title

    def test_create_event_success(self, client, sample_event_data):
        """Test creating a new event successfully."""
        with patch('app.services.dynamodb_service.DynamoDBService.create_event', return_value=sample_event_data):
            response = client.post('/api/events/',
                                 data=json.dumps(sample_event_data),
                                 content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['title'] == sample_event_data['title']
            assert data['description'] == sample_event_data['description']

    def test_create_event_missing_required_fields(self, client):
        """Test creating an event with missing required fields."""
        incomplete_data = {
            "title": "Test Meeting",
            "description": "A test meeting"
            # Missing start_time and end_time
        }
        
        response = client.post('/api/events/',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_event_invalid_json(self, client):
        """Test creating an event with invalid JSON."""
        response = client.post('/api/events/',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 500

    def test_update_event_success(self, client, sample_event):
        """Test updating an existing event successfully."""
        update_data = {
            "title": "Updated Meeting",
            "description": "Updated description",
            "start_time": sample_event.start_time,
            "end_time": sample_event.end_time,
            "recurrence": sample_event.recurrence,
            "email": sample_event.email
        }
        updated_event = sample_event.to_dict()
        updated_event.update(update_data)
        with patch('app.services.dynamodb_service.DynamoDBService.get_event_by_id', return_value=sample_event.to_dict()), \
             patch('app.services.dynamodb_service.DynamoDBService.update_event', return_value=updated_event):
            response = client.put(f'/api/events/{sample_event.id}',
                                data=json.dumps(update_data),
                                content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['title'] == update_data['title']

    def test_update_event_not_found(self, client):
        """Test updating a non-existent event."""
        update_data = {"title": "Updated Meeting"}
        
        response = client.put('/api/events/nonexistent-id',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_partial_update_event_success(self, client, sample_event):
        """Test partially updating an existing event."""
        update_data = {"title": "Partially Updated Meeting"}
        updated_event = sample_event.to_dict()
        updated_event.update(update_data)
        with patch('app.services.dynamodb_service.DynamoDBService.get_event_by_id', return_value=sample_event.to_dict()), \
             patch('app.services.dynamodb_service.DynamoDBService.update_event', return_value=updated_event):
            response = client.patch(f'/api/events/{sample_event.id}',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['title'] == update_data['title']
            assert data['description'] == sample_event.description  # Should remain unchanged

    def test_delete_event_success(self, client, sample_event):
        """Test deleting an existing event successfully."""
        with patch('app.services.dynamodb_service.DynamoDBService.delete_event', return_value=True):
            response = client.delete(f'/api/events/{sample_event.id}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Event deleted'

    def test_delete_event_not_found(self, client):
        """Test deleting a non-existent event."""
        response = client.delete('/api/events/nonexistent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_search_events_success(self, client, sample_event):
        """Test searching events successfully."""
        with patch('app.services.dynamodb_service.DynamoDBService.search_events', return_value=[sample_event.to_dict()]):
            response = client.get('/api/events/search?q=meeting')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['title'] == sample_event.title

    def test_search_events_no_query(self, client):
        """Test searching events without providing a query parameter."""
        response = client.get('/api/events/search')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_search_events_empty_query(self, client):
        """Test searching events with an empty query parameter."""
        response = client.get('/api/events/search?q=')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_search_events_no_results(self, client, sample_event):
        """Test searching events that return no results."""
        with patch('app.services.dynamodb_service.DynamoDBService.search_events', return_value=[]):
            response = client.get('/api/events/search?q=nonexistent')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 0

    def test_swagger_documentation_available(self, client):
        """Test that Swagger documentation is available."""
        response = client.get('/apispec_1.json')
        assert response.status_code == 200

    def test_event_model_creation(self, sample_event_data):
        """Test Event model creation and serialization."""
        event = Event(
            title=sample_event_data["title"],
            description=sample_event_data["description"],
            start_time=sample_event_data["start_time"],
            end_time=sample_event_data["end_time"],
            recurrence=sample_event_data["recurrence"],
            email=sample_event_data["email"]
        )
        
        assert event.title == sample_event_data["title"]
        assert event.description == sample_event_data["description"]
        assert event.start_time == sample_event_data["start_time"]
        assert event.end_time == sample_event_data["end_time"]
        assert event.recurrence == sample_event_data["recurrence"]
        assert event.email == sample_event_data["email"]
        assert event.id is not None

    def test_event_model_to_dict(self, sample_event):
        """Test Event model serialization to dictionary."""
        event_dict = sample_event.to_dict()
        
        assert isinstance(event_dict, dict)
        assert event_dict['title'] == sample_event.title
        assert event_dict['description'] == sample_event.description
        assert event_dict['start_time'] == sample_event.start_time
        assert event_dict['end_time'] == sample_event.end_time
        assert event_dict['recurrence'] == sample_event.recurrence
        assert event_dict['email'] == sample_event.email
        assert event_dict['id'] == sample_event.id

    def test_service_get_all_events(self, sample_event):
        """Test the get_all_events service function."""
        with patch('app.services.dynamodb_service.DynamoDBService.get_all_events', return_value=[sample_event.to_dict()]):
            events = get_all_events()
            assert len(events) == 1
            assert events[0]['title'] == sample_event.title

    def test_service_create_event(self, sample_event_data):
        """Test the create_event service function."""
        with patch('app.services.dynamodb_service.DynamoDBService.create_event', return_value=sample_event_data):
            new_event = create_event(sample_event_data)
            assert new_event['title'] == sample_event_data['title']
            assert new_event['description'] == sample_event_data['description']

    def test_service_update_event(self, sample_event):
        """Test the update_event service function."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "start_time": sample_event.start_time,
            "end_time": sample_event.end_time,
            "recurrence": sample_event.recurrence,
            "email": sample_event.email
        }
        updated_event = sample_event.to_dict()
        updated_event.update(update_data)
        with patch('app.services.dynamodb_service.DynamoDBService.update_event', return_value=updated_event):
            updated_event_result = update_event(sample_event.id, update_data)
            assert updated_event_result['title'] == update_data['title']

    def test_service_delete_event(self, sample_event):
        """Test the delete_event service function."""
        with patch('app.services.dynamodb_service.DynamoDBService.delete_event', return_value=True):
            result = delete_event(sample_event.id)
            assert result is True

    def test_service_search_event(self, sample_event):
        """Test the search_event service function."""
        with patch('app.services.dynamodb_service.DynamoDBService.search_events', return_value=[sample_event.to_dict()]):
            results = search_event("meeting")
            assert len(results) == 1
            assert results[0]['title'] == sample_event.title


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 