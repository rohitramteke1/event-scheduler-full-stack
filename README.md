# 📅 Event Scheduler - Backend & Streamlit UI

A robust, full-stack event scheduling application featuring a Flask REST API backend, a modern Streamlit UI frontend, and AWS DynamoDB/S3 integration for scalable, cloud-native data storage.

---

## 📚 Documentation

- [Deployment Guide (AWS)](docs/AWS_DEPLOYMENT.md)
- [Streamlit UI Guide](docs/README_streamlit-ui.md)

For all additional documentation, see the [docs/](docs/) folder.

---

## 🚀 Features

- **Event Management:** Create, update, delete, and search events with support for recurrence and email reminders.
- **Modern UI:** Intuitive Streamlit interface for event creation, management, and analytics.
- **Email Reminders:** Automatic email notifications for upcoming events via Brevo SMTP.
- **Recurring Events:** Support for daily, weekly, and monthly recurring events.
- **Cloud-Native:** Uses AWS DynamoDB for event storage and S3 for future backup/export.
- **API-First:** RESTful API with Swagger documentation.
- **Production-Ready:** Includes deployment guides for AWS EC2 and Docker.
- **Comprehensive Testing:** Pytest suite for backend logic and API endpoints.

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   Flask API     │    │   AWS Services  │
│   (Port 8501)   │◄──►│   (Port 5000)   │◄──►│   DynamoDB      │
└─────────────────┘    └─────────────────┘    │   + S3          │
                                              └─────────────────┘
```

---

## 📁 Project Structure

```
event-scheduler-backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   └── event_model.py
│   ├── routes/
│   │   └── event_routes.py
│   ├── services/
│   │   ├── event_service.py
│   │   └── dynamodb_service.py
│   ├── tasks/
│   │   └── reminder_task.py
│   └── utils/
│       ├── email_utils.py
│       └── file_io.py
├── streamlit-ui/
│   ├── main.py
│   ├── requirements.txt
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── create_event.py
│   │   ├── view_events.py
│   │   └── search_events.py
│   └── utils/
│       └── api_client.py
├── tests/
│   └── test_app.py
├── requirements.txt
├── run.py
├── migrate_to_dynamodb.py
├── AWS_DEPLOYMENT.md
└── README.md
```

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8+
- AWS account (for DynamoDB/S3)
- [AWS CLI](https://aws.amazon.com/cli/) configured
- (Optional) Docker

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd event-scheduler-backend
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend (Streamlit UI) Dependencies

```bash
cd streamlit-ui
pip install -r requirements.txt
cd ..
```

### 4. Configure Environment

Edit `.env` with your AWS and email settings. Example:

```
AWS_DEFAULT_REGION=ap-south-1
DYNAMODB_TABLE_NAME=event-sheduler-db
S3_BUCKET_NAME=event-scheduler-backup
# Brevo SMTP Email Configuration
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USER=your_brevo_email
EMAIL_PASS=your_brevo_smtp_key
EMAIL_FROM=your_email
EMAIL_TO=recipient_email
```

---

## 🧪 Running Tests

Run the backend test suite from the project root:

```bash
pytest -v tests/test_app.py
```

---

## 🏃 Running the Application

### 1. Start the Flask API

```bash
python run.py
```

### 2. Start the Streamlit UI

```bash
cd streamlit-ui
streamlit run main.py
# streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🌐 API Endpoints

For full details, see the [API Reference](docs/API_REFERENCE.md).

| Method | Path                       | Description                  |
|--------|----------------------------|------------------------------|
| GET    | /api/events/               | List all events              |
| POST   | /api/events/               | Create a new event           |
| GET    | /api/events/<id>           | Get event by ID              |
| PUT    | /api/events/<id>           | Update all fields of event   |
| PATCH  | /api/events/<id>           | Partial update of event      |
| DELETE | /api/events/<id>           | Delete event by ID           |
| GET    | /api/events/search?q=...   | Search events                |

- All endpoints return JSON.
- See [Swagger UI](http://localhost:5000/apidocs/) for interactive docs.

---