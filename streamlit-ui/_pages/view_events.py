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
    st.markdown("""
<style>
/* Only use box-sizing: border-box on custom containers. Let Streamlit control width. */
body { overflow-x: hidden; }
.card {
  border: 1.5px solid #22283122;
  border-radius: 15px;
  padding: 1.5rem 1.2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,180,216,0.07);
  background: none;
  box-sizing: border-box;
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
</style>
    """, unsafe_allow_html=True)
    st.markdown("""
<h2 style='display:flex;align-items:center;'>
  <span style='vertical-align:middle;display:inline-block;margin-right:8px;'>
    <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='9' y1='9' x2='15' y2='9'/><line x1='9' y1='13' x2='15' y2='13'/><line x1='9' y1='17' x2='15' y2='17'/></svg>
  </span>View All Events
</h2>
    """, unsafe_allow_html=True)
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
                if status_filter == "Upcoming" and "Upcoming" not in status:
                    continue
                elif status_filter == "Ongoing" and "Ongoing" not in status:
                    continue
                elif status_filter == "Past" and "Past" not in status:
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
        
        # --- Only show event list if not in edit or delete mode ---
        if not st.session_state.get('edit_mode', False) and not st.session_state.get('delete_mode', False):
            st.markdown(f"""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><line x1='9' y1='9' x2='15' y2='9'/><line x1='9' y1='13' x2='15' y2='13'/><line x1='9' y1='17' x2='15' y2='17'/></svg>
  Events ({len(filtered_events)} found)
</div>
        """, unsafe_allow_html=True)
            
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
                        calendar_svg = """
                        <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle;margin-right:4px;'>
                          <rect x='3' y='4' width='18' height='18' rx='2' ry='2'/>
                          <line x1='16' y1='2' x2='16' y2='6'/>
                          <line x1='8' y1='2' x2='8' y2='6'/>
                          <line x1='3' y1='10' x2='21' y2='10'/>
                        </svg>
                        """
                        clock_svg = """
                        <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle;margin-right:4px;'>
                          <circle cx='12' cy='12' r='10'/>
                          <polyline points='12 6 12 12 16 14'/>
                        </svg>
                        """
                        st.markdown(f"{calendar_svg} {format_datetime(event['start_time'])}", unsafe_allow_html=True)
                        st.markdown(f"{clock_svg} {format_datetime(event['end_time'])}", unsafe_allow_html=True)
                    with col3:
                        status = get_event_status(event)
                        st.markdown(status)
                    with col4:
                        if st.button('✏️ Edit', key=f"edit_{event['id']}"):
                            st.session_state.edit_event_id = event['id']
                            st.session_state.edit_mode = True
                            st.rerun()
                        if st.button('🗑️ Delete', key=f"delete_{event['id']}"):
                            st.session_state.delete_event_id = event['id']
                            st.session_state.delete_mode = True
                            st.rerun()
                    st.markdown("---")
        # --- End event list block ---
        
        # Edit and delete forms remain as before, but now are always at the top
        if st.session_state.get('edit_mode', False):
            event_id = st.session_state.edit_event_id
            event = api_client.get_event_by_id(event_id)
            st.markdown("""
    <style>
    /* Style the Save Changes button in the form */
    button[kind="primary"]:has(span:contains('Save Changes')) {
        background-color: #FF3B30 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.5rem !important;
        font-size: 1.08rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        margin-top: 0.5rem;
    }
    button[kind="primary"]:has(span:contains('Save Changes')):hover {
        background-color: #d32f2f !important;
    }
    </style>
    """, unsafe_allow_html=True)
            st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><path d='M12 20h9'/><path d='M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19.5 3 21l1.5-4L16.5 3.5z'/></svg>
  Edit Event
</div>
            """, unsafe_allow_html=True)
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
                    save_clicked = st.form_submit_button("Save Changes")
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.edit_mode = False
                        st.rerun()
                if save_clicked:
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
        if st.session_state.get('delete_mode', False):
            event_id = st.session_state.delete_event_id
            event = api_client.get_event_by_id(event_id)
            st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><polyline points='3 6 5 6 21 6'/><path d='M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2'/><line x1='10' y1='11' x2='10' y2='17'/><line x1='14' y1='11' x2='14' y2='17'/></svg>
  Delete Event
</div>
            """, unsafe_allow_html=True)
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
        st.sidebar.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.08em;margin-bottom:0.5em;'>
  <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:6px;'><path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/><polyline points='7 10 12 15 17 10'/><line x1='12' y1='15' x2='12' y2='3'/></svg>
  Export
</div>
        """, unsafe_allow_html=True)
        
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