import streamlit as st
from datetime import datetime, timedelta
import sys
import os
import re

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_client import EventAPIClient

def create_event_page():
    st.markdown("""
<style>
/* Centered card for modern, clean UI */
.centered-card {
  max-width: 700px;
  margin: 2.5rem auto;
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid #22283122;
  border-radius: 15px;
  padding: 1.5rem 1.2rem;
  box-shadow: 0 2px 12px rgba(0,180,216,0.07);
  background: none;
}
.section-heading {
  display: flex;
  align-items: center;
  font-size: 1.18em;
  font-weight: bold;
  margin-bottom: 1.2rem;
  letter-spacing: 0.5px;
  color: #222831;
}
.section-heading svg {
  margin-right: 10px;
  vertical-align: middle;
  stroke: #00B4D8;
}
.feature-box {
  border: 1.2px solid #00B4D8;
  border-radius: 13px;
  padding: 1.2rem 1rem;
  margin-bottom: 1.2rem;
  background: none;
  box-sizing: border-box;
}
body { overflow-x: hidden; }
</style>
""", unsafe_allow_html=True)

    # Initialize API client
    try:
        api_client = EventAPIClient()
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")
        return
    
    with st.form("create_event_form"):
        # Add a centered 'Create New Event' title at the top of the card
        st.markdown("""
        <div style='text-align:center;margin-bottom:1.5rem;'>
          <span style='font-size:2rem;font-weight:700;letter-spacing:0.5px;'>Create New Event</span>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            title = st.text_input("Event Title *", placeholder="Enter event title")
        with col2:
            description = st.text_area("Description *", placeholder="Enter event description", height=100)
        # --- Date & Time Section ---
        st.markdown("""
        <div class='section-heading'>
          <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
          Date & Time
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            default_date = datetime.now().date()
            event_date = st.date_input("Event Date *", value=default_date)
        with col2:
            default_time = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
            start_time_str = st.text_input("Start Time (24h, e.g., 13:07)", value=default_time, key="start_time_text")
        with col3:
            default_end_time = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
            end_time_str = st.text_input("End Time (24h, e.g., 13:07)", value=default_end_time, key="end_time_text")
        # --- Additional Settings Section ---
        st.markdown("""
        <div class='section-heading'>
          <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><path d='M12 8v4l3 3'/></svg>
          Additional Settings
        </div>
        """, unsafe_allow_html=True)
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
        # --- Submit Button ---
        submitted = st.form_submit_button("Create Event", type="primary")
        if submitted:
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
            start_datetime = datetime.combine(event_date, start_time)
            end_datetime = datetime.combine(event_date, end_time)
            event_data = {
                "title": title,
                "description": description,
                "start_time": start_datetime.isoformat(),
                "end_time": end_datetime.isoformat(),
                "recurrence": recurrence,
                "email": email
            }
            try:
                new_event = api_client.create_event(event_data)
                st.success("✅ Event created successfully!")
                st.balloons()
                with st.expander("View Created Event", expanded=True):
                    st.json(new_event)
            except Exception as e:
                st.error(f"Failed to create event: {str(e)}")
    # --- Help Section ---
    with st.expander("ℹ️ Help", expanded=False):
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