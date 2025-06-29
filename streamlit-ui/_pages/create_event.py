import streamlit as st
from datetime import datetime, timedelta
import sys
import os
import re

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_client import EventAPIClient

def create_event_page():
    st.header("📅 Create New Event")
    st.markdown("---")
    
    # Initialize API client
    try:
        api_client = EventAPIClient()
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")
        return
    
    # Event creation form
    with st.form("create_event_form"):
        st.subheader("Event Details")
        
        # Title and Description
        col1, col2 = st.columns([1, 1])
        with col1:
            title = st.text_input("Event Title *", placeholder="Enter event title")
        with col2:
            description = st.text_area("Description *", placeholder="Enter event description", height=100)
        
        # Date and Time
        st.subheader("Date & Time")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            # Default to today
            default_date = datetime.now().date()
            event_date = st.date_input("Event Date *", value=default_date)
        
        with col2:
            default_time = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
            start_time_str = st.text_input("Start Time (24h, e.g., 13:07)", value=default_time, key="start_time_text")
        
        with col3:
            default_end_time = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
            end_time_str = st.text_input("End Time (24h, e.g., 13:07)", value=default_end_time, key="end_time_text")
        
        # Recurrence and Email
        st.subheader("Additional Settings")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            recurrence_options = ["None", "daily", "weekly", "monthly"]
            recurrence = st.selectbox("Recurrence", recurrence_options)
            if recurrence == "None":
                recurrence = None
        
        with col2:
            email = st.text_input("Email for Reminders", placeholder="your@email.com")
            if email == "":
                email = None
        
        # Submit button
        submitted = st.form_submit_button("Create Event", type="primary")
        
        if submitted:
            # Validation
            time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
            if not title or not description:
                st.error("Title and description are required!")
                return
            if not re.match(time_pattern, start_time_str):
                st.error("Start time must be in 24-hour format (e.g., 13:07)")
                return
            if not re.match(time_pattern, end_time_str):
                st.error("End time must be in 24-hour format (e.g., 13:07)")
                return
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            if start_time >= end_time:
                st.error("End time must be after start time!")
                return
            
            # Combine date and time
            start_datetime = datetime.combine(event_date, start_time)
            end_datetime = datetime.combine(event_date, end_time)
            
            # Prepare event data
            event_data = {
                "title": title,
                "description": description,
                "start_time": start_datetime.isoformat(),
                "end_time": end_datetime.isoformat(),
                "recurrence": recurrence,
                "email": email
            }
            
            try:
                # Create event
                new_event = api_client.create_event(event_data)
                
                st.success("✅ Event created successfully!")
                st.balloons()
                
                # Show created event details
                with st.expander("View Created Event", expanded=True):
                    st.json(new_event)
                
                # Clear form (Streamlit will handle this automatically)
                
            except Exception as e:
                st.error(f"Failed to create event: {str(e)}")
    
    # Help section
    with st.expander("ℹ️ Help"):
        st.markdown("""
        **Required Fields:**
        - **Title**: A brief name for your event
        - **Description**: Details about the event
        - **Date**: When the event will take place
        - **Start Time**: When the event begins
        - **End Time**: When the event ends
        
        **Optional Fields:**
        - **Recurrence**: How often the event repeats
        - **Email**: Receive email reminders for this event
        
        **Tips:**
        - End time must be after start time
        - Email reminders will be sent 1 hour before the event
        - Recurring events will automatically create future instances
        """)

if __name__ == "__main__":
    create_event_page() 