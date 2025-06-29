# 📅 Event Scheduler - Streamlit UI

A beautiful and intuitive web interface for the Event Scheduler application, built with Streamlit.

## 🚀 Features

- **📊 Interactive Dashboard** - Visual statistics and event timelines
- **➕ Easy Event Creation** - User-friendly forms with date/time pickers
- **📋 Event Management** - View, edit, and delete events with filtering
- **🔍 Advanced Search** - Quick and advanced search with multiple filters
- **📧 Email Reminders** - Automatic notifications for upcoming events
- **🔄 Recurring Events** - Support for daily, weekly, and monthly events
- **📤 Export Options** - Export events to CSV and JSON formats
- **📱 Responsive Design** - Works on desktop and mobile devices

## 🛠️ Installation

### Prerequisites

1. **Flask Backend Running**: Make sure your Flask API is running on `http://localhost:5000`
2. **Python 3.8+**: Required for Streamlit

### Setup

1. **Navigate to the Streamlit UI directory**:
   ```bash
   cd streamlit-ui
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**:
   ```bash
   streamlit run main.py
   ```

4. **Open your browser** and go to `http://localhost:8501`

## 📖 Usage Guide

### 🏠 Home Page
- **Overview**: Quick statistics and today's events
- **Features**: Overview of all available features
- **Quick Actions**: Direct access to main functions
- **Getting Started**: Step-by-step guide for new users

### 📊 Dashboard
- **Key Metrics**: Total events, upcoming, ongoing, and past events
- **Charts**: Visual representation of event status distribution
- **Timeline**: Interactive timeline of upcoming events
- **Quick Actions**: Easy navigation to other pages

### ➕ Create Event
- **Event Details**: Title and description
- **Date & Time**: Date picker and time inputs
- **Additional Settings**: Recurrence and email reminders
- **Validation**: Real-time form validation

### 📋 View Events
- **Filters**: Status, date range, recurrence, and search
- **Sorting**: Sort by start time, title, or status
- **Actions**: Edit and delete events inline
- **Export**: Download events as CSV

### 🔍 Search Events
- **Quick Search**: Simple keyword search
- **Advanced Search**: Multiple filters and criteria
- **Results**: Formatted search results with actions
- **Export**: Export search results to CSV or JSON

## 🔧 Configuration

### API Connection
The UI connects to your Flask API at `http://localhost:5000` by default. To change this:

1. Edit `utils/api_client.py`
2. Modify the `base_url` parameter in the `EventAPIClient` constructor

### Customization
- **Styling**: Modify the CSS in `main.py` for custom styling
- **Features**: Add new pages in the `pages/` directory
- **API**: Extend the `EventAPIClient` class for additional API calls

## 📁 Project Structure

```
streamlit-ui/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── utils/
│   ├── __init__.py
│   └── api_client.py      # API communication client
└── pages/
    ├── __init__.py
    ├── dashboard.py       # Analytics dashboard
    ├── create_event.py    # Event creation form
    ├── view_events.py     # Event management
    └── search_events.py   # Search functionality
```

## 🎨 UI Components

### Navigation
- **Sidebar Navigation**: Easy switching between pages
- **API Status**: Real-time connection status indicator
- **Quick Actions**: Direct access to common functions

### Forms
- **Date/Time Pickers**: Intuitive date and time selection
- **Validation**: Real-time form validation with error messages
- **Auto-save**: Automatic form state management

### Data Display
- **Cards**: Clean event display with status indicators
- **Tables**: Sortable and filterable event lists
- **Charts**: Interactive visualizations with Plotly

### Actions
- **Inline Editing**: Edit events without page navigation
- **Bulk Operations**: Export and manage multiple events
- **Confirmation Dialogs**: Safe delete operations

## 🔌 API Integration

The Streamlit UI communicates with your Flask backend through RESTful API calls:

- **GET /api/events/** - Retrieve all events
- **POST /api/events/** - Create new events
- **PUT /api/events/{id}** - Update events
- **PATCH /api/events/{id}** - Partial updates
- **DELETE /api/events/{id}** - Delete events
- **GET /api/events/search** - Search events

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: Start Flask API
cd ../
python run.py

# Terminal 2: Start Streamlit UI
cd streamlit-ui
streamlit run main.py
```

### Production Deployment
1. **Streamlit Cloud**: Deploy directly to Streamlit Cloud
2. **Docker**: Create a Docker container for the UI
3. **VPS**: Deploy on a virtual private server

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Error**
   - Ensure Flask backend is running on port 5000
   - Check firewall settings
   - Verify API endpoints are accessible

2. **Import Errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Page Navigation Issues**
   - Clear browser cache
   - Restart Streamlit application

### Debug Mode
Run Streamlit with debug information:
```bash
streamlit run main.py --logger.level debug
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Event Scheduler application. See the main project for license information.

## 🤝 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Create an issue in the repository

---

**Happy Event Scheduling! 🎉** 