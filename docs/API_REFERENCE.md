# 📖 API Reference

This document describes all available API endpoints for the Event Scheduler backend.

---

## Base URL

```
http://<your-server>:5000/api/events/
```

---

## Endpoints

### 1. List All Events
- **GET** `/api/events/`
- **Description:** Get all events
- **Response:** `200 OK` (JSON array of events)

### 2. Create Event
- **POST** `/api/events/`
- **Description:** Create a new event
- **Body:**
```json
{
  "title": "Team Meeting",
  "description": "Discuss project status",
  "start_time": "2025-07-01T10:00:00",
  "end_time": "2025-07-01T11:00:00",
  "recurrence": "weekly", // optional: "daily", "weekly", "monthly", or null
  "email": "user@example.com" // optional
}
```
- **Response:** `201 Created` (JSON of created event)

### 3. Get Event by ID
- **GET** `/api/events/<event_id>`
- **Description:** Get a single event by its ID
- **Response:** `200 OK` (JSON of event) or `404 Not Found`

### 4. Update Event (Full)
- **PUT** `/api/events/<event_id>`
- **Description:** Update all fields of an event
- **Body:** (same as create)
- **Response:** `200 OK` (JSON of updated event) or `404 Not Found`

### 5. Update Event (Partial)
- **PATCH** `/api/events/<event_id>`
- **Description:** Update only specified fields
- **Body:** (any subset of event fields)
- **Response:** `200 OK` (JSON of updated event) or `404 Not Found`

### 6. Delete Event
- **DELETE** `/api/events/<event_id>`
- **Description:** Delete an event by ID
- **Response:** `200 OK` (JSON message) or `404 Not Found`

### 7. Search Events
- **GET** `/api/events/search?q=<query>`
- **Description:** Search events by title or description
- **Response:** `200 OK` (JSON array of matching events)

---

## Example Event Object
```json
{
  "id": "uuid-string",
  "title": "Team Meeting",
  "description": "Discuss project status",
  "start_time": "2025-07-01T10:00:00",
  "end_time": "2025-07-01T11:00:00",
  "recurrence": "weekly",
  "email": "user@example.com"
}
```

---

## Error Responses
- `400 Bad Request`: Invalid input or missing required fields
- `404 Not Found`: Event not found
- `500 Internal Server Error`: Unexpected server error

---

## Interactive API Docs
- Swagger UI: [http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)

---

For more details, see the main [README.md](../README.md) or the [Deployment Guide](AWS_DEPLOYMENT.md). 