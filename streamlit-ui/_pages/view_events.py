import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import re

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_client import EventAPIClient

def format_datetime(dt_str):
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def get_event_status(event):
    """Get the status of an event (upcoming, ongoing, past)"""
    try:
        start_time = datetime.fromisoformat(event['start_time'])
        end_time = datetime.fromisoformat(event['end_time'])
        now = datetime.now()
        
        if now < start_time:
            return "🟢 Upcoming"
        elif start_time <= now <= end_time:
            return "🟡 Ongoing"
        else:
            return "🔴 Past"
    except:
        return "❓ Unknown"

def view_events_page():
    st.header("📋 View All Events")
    st.markdown("---")
    
    # Initialize API client
    try:
        api_client = EventAPIClient()
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")
        return
    
    # Clear filters if navigating from search to edit/delete
    if (st.session_state.get('edit_mode', False) or st.session_state.get('delete_mode', False)):
        st.session_state['search_query'] = ''
        st.session_state['status_filter'] = 'All'
        st.session_state['recurrence_filter'] = 'All'
        st.session_state['start_date'] = datetime.now().date() - timedelta(days=7)
        st.session_state['end_date'] = datetime.now().date() + timedelta(days=30)

    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Status filter
    status_filter = st.sidebar.selectbox(
        "Filter by Status",
        ["All", "Upcoming", "Ongoing", "Past"],
        key='status_filter'
    )
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if 'start_date' not in st.session_state:
            st.session_state['start_date'] = datetime.now().date() - timedelta(days=7)
        start_date = st.date_input("From", key='start_date')
    with col2:
        if 'end_date' not in st.session_state:
            st.session_state['end_date'] = datetime.now().date() + timedelta(days=30)
        end_date = st.date_input("To", key='end_date')
    
    # Recurrence filter
    recurrence_filter = st.sidebar.selectbox(
        "Filter by Recurrence",
        ["All", "None", "daily", "weekly", "monthly"],
        key='recurrence_filter'
    )
    
    # Search box
    search_query = st.sidebar.text_input("🔍 Search Events", placeholder="Search by title or description", key='search_query')
    
    try:
        # Get events based on search
        if search_query:
            events = api_client.search_events(search_query)
        else:
            events = api_client.get_all_events()
        
        if not events:
            st.info("No events found. Create your first event!")
            return
        
        # Apply filters
        filtered_events = []
        for event in events:
            # Status filter
            status = get_event_status(event)
            if status_filter != "All":
                if status_filter == "Upcoming" and "🟢" not in status:
                    continue
                elif status_filter == "Ongoing" and "🟡" not in status:
                    continue
                elif status_filter == "Past" and "🔴" not in status:
                    continue
            
            # Date range filter
            try:
                event_date = datetime.fromisoformat(event['start_time']).date()
                if event_date < start_date or event_date > end_date:
                    continue
            except:
                continue
            
            # Recurrence filter
            if recurrence_filter != "All":
                event_recurrence = event.get('recurrence') or "None"
                if event_recurrence != recurrence_filter:
                    continue
            
            filtered_events.append(event)
        
        if not filtered_events:
            st.warning("No events match your current filters.")
            return
        
        # Display events
        st.subheader(f"📊 Events ({len(filtered_events)} found)")
        
        # Sort options
        col1, col2 = st.columns([1, 3])
        with col1:
            sort_by = st.selectbox("Sort by", ["Start Time", "Title", "Status"])
        
        # Sort events
        if sort_by == "Start Time":
            filtered_events.sort(key=lambda x: x['start_time'])
        elif sort_by == "Title":
            filtered_events.sort(key=lambda x: x['title'].lower())
        elif sort_by == "Status":
            filtered_events.sort(key=lambda x: get_event_status(x))
        
        # Display events in a table
        for event in filtered_events:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{event['title']}**")
                    st.caption(event['description'])
                    if event.get('recurrence'):
                        st.caption(f"🔄 Recurring: {event['recurrence']}")
                
                with col2:
                    st.text(f"📅 {format_datetime(event['start_time'])}")
                    st.text(f"⏰ {format_datetime(event['end_time'])}")
                
                with col3:
                    status = get_event_status(event)
                    st.markdown(status)
                
                with col4:
                    # Use unique keys and set session state + rerun
                    if st.button("✏️ Edit", key=f"edit_{event['id']}"):
                        st.session_state.edit_event_id = event['id']
                        st.session_state.edit_mode = True
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"delete_{event['id']}"):
                        st.session_state.delete_event_id = event['id']
                        st.session_state.delete_mode = True
                        st.rerun()
                
                st.markdown("---")
        
        # Move edit/delete UI outside the loop
        if st.session_state.get('edit_mode', False):
            event_id = st.session_state.edit_event_id
            event = api_client.get_event_by_id(event_id)
            st.subheader("✏️ Edit Event")
            with st.form("edit_event_form"):
                title = st.text_input("Title", value=event['title'])
                description = st.text_area("Description", value=event['description'])
                start_dt = datetime.fromisoformat(event['start_time'])
                end_dt = datetime.fromisoformat(event['end_time'])
                col1, col2, col3 = st.columns(3)
                with col1:
                    start_date = st.date_input("Start Date", value=start_dt.date())
                with col2:
                    start_time_str = st.text_input("Start Time (24h, e.g., 13:07)", value=start_dt.strftime("%H:%M"), key="edit_start_time_text")
                with col3:
                    end_time_str = st.text_input("End Time (24h, e.g., 13:07)", value=end_dt.strftime("%H:%M"), key="edit_end_time_text")
                recurrence_options = ["None", "daily", "weekly", "monthly"]
                current_recurrence = event.get('recurrence') or "None"
                recurrence = st.selectbox("Recurrence", recurrence_options, 
                                        index=recurrence_options.index(current_recurrence))
                if recurrence == "None":
                    recurrence = None
                email = st.text_input("Email", value=event.get('email', ''))
                if email == "":
                    email = None
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Save Changes"):
                        # Validation
                        time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
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
                        try:
                            start_datetime = datetime.combine(start_date, start_time)
                            end_datetime = datetime.combine(start_date, end_time)
                            update_data = {
                                "title": title,
                                "description": description,
                                "start_time": start_datetime.isoformat(),
                                "end_time": end_datetime.isoformat(),
                                "recurrence": recurrence,
                                "email": email
                            }
                            api_client.update_event(event['id'], update_data)
                            st.success("✅ Event updated successfully!")
                            st.session_state.edit_mode = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update event: {str(e)}")
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.edit_mode = False
                        st.rerun()
        if st.session_state.get('delete_mode', False):
            event_id = st.session_state.delete_event_id
            event = api_client.get_event_by_id(event_id)
            st.subheader("🗑️ Delete Event")
            st.warning(f"Are you sure you want to delete '{event['title']}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete"):
                    try:
                        api_client.delete_event(event['id'])
                        st.success("✅ Event deleted successfully!")
                        st.session_state.delete_mode = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete event: {str(e)}")
            with col2:
                if st.button("Cancel"):
                    st.session_state.delete_mode = False
                    st.rerun()
        
        # Export options
        st.sidebar.markdown("---")
        st.sidebar.subheader("📤 Export")
        
        if st.sidebar.button("Export to CSV"):
            # Prepare data for CSV
            csv_data = []
            for event in filtered_events:
                csv_data.append({
                    'Title': event['title'],
                    'Description': event['description'],
                    'Start Time': format_datetime(event['start_time']),
                    'End Time': format_datetime(event['end_time']),
                    'Recurrence': event.get('recurrence', 'None'),
                    'Email': event.get('email', ''),
                    'Status': get_event_status(event)
                })
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False)
            st.sidebar.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Failed to load events: {str(e)}")

if __name__ == "__main__":
    view_events_page() 