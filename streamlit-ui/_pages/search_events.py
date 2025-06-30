import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

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

def search_events_page():
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
    <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'/><line x1='21' y1='21' x2='16.65' y2='16.65'/></svg>
  </span>Search Events
</h2>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize API client
    try:
        api_client = EventAPIClient()
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")
        return
    
    # Search interface
    st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><circle cx='11' cy='11' r='8'/><line x1='21' y1='21' x2='16.65' y2='16.65'/></svg>
  Search Options
</div>
    """, unsafe_allow_html=True)
    
    # Search method selection
    search_method = st.radio(
        "Choose search method:",
        ["Quick Search", "Advanced Search"],
        horizontal=True
    )
    
    if search_method == "Quick Search":
        # Simple search
        search_query = st.text_input(
            "🔍 Search Events",
            placeholder="Enter keywords to search in title or description..."
        )
        
        if st.button("Search", type="primary"):
            if search_query.strip():
                try:
                    results = api_client.search_events(search_query)
                    display_search_results(results, search_query)
                except Exception as e:
                    st.error(f"Search failed: {str(e)}")
            else:
                st.warning("Please enter a search query.")
    
    else:
        # Advanced search
        st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.08em;margin-bottom:0.5em;'>
  <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:6px;'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><line x1='9' y1='9' x2='15' y2='9'/><line x1='9' y1='13' x2='15' y2='13'/><line x1='9' y1='17' x2='15' y2='17'/></svg>
  Advanced Search Filters
</div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Text search
            title_search = st.text_input("Title contains:", placeholder="Search in title...")
            description_search = st.text_input("Description contains:", placeholder="Search in description...")
            
            # Date range
            st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.08em;margin-bottom:0.5em;'>
  <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:6px;'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
  Date Range
</div>
            """, unsafe_allow_html=True)
            start_date = st.date_input("From date:", value=datetime.now().date() - timedelta(days=30))
            end_date = st.date_input("To date:", value=datetime.now().date() + timedelta(days=30))
        
        with col2:
            # Status filter
            status_filter = st.selectbox("Event Status:", ["All", "Upcoming", "Ongoing", "Past"])
            
            # Recurrence filter
            recurrence_filter = st.selectbox("Recurrence:", ["All", "None", "daily", "weekly", "monthly"])
            
            # Email filter
            email_filter = st.selectbox("Email Reminders:", ["All", "With Email", "Without Email"])
            
            # Time range
            st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.08em;margin-bottom:0.5em;'>
  <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:6px;'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>
  Time Range
</div>
            """, unsafe_allow_html=True)
            start_time = st.time_input("From time (24h)", value=datetime.now().time(), step=timedelta(minutes=1), help="You can type any time in 24-hour format (e.g., 13:07)")
            end_time = st.time_input("To time (24h)", value=(datetime.now() + timedelta(hours=23)).time(), step=timedelta(minutes=1), help="You can type any time in 24-hour format (e.g., 13:07)")
        
        if st.button("Advanced Search", type="primary"):
            try:
                # Get all events first
                all_events = api_client.get_all_events()
                
                # Apply filters
                filtered_events = []
                
                for event in all_events:
                    # Text search
                    if title_search and title_search.lower() not in event['title'].lower():
                        continue
                    if description_search and description_search.lower() not in event['description'].lower():
                        continue
                    
                    # Date range filter
                    try:
                        event_date = datetime.fromisoformat(event['start_time']).date()
                        if event_date < start_date or event_date > end_date:
                            continue
                    except:
                        continue
                    
                    # Time range filter
                    try:
                        event_time = datetime.fromisoformat(event['start_time']).time()
                        if event_time < start_time or event_time > end_time:
                            continue
                    except:
                        continue
                    
                    # Status filter
                    status = get_event_status(event)
                    if status_filter != "All":
                        if status_filter == "Upcoming" and "🟢" not in status:
                            continue
                        elif status_filter == "Ongoing" and "🟡" not in status:
                            continue
                        elif status_filter == "Past" and "🔴" not in status:
                            continue
                    
                    # Recurrence filter
                    if recurrence_filter != "All":
                        event_recurrence = event.get('recurrence') or "None"
                        if event_recurrence != recurrence_filter:
                            continue
                    
                    # Email filter
                    if email_filter != "All":
                        has_email = bool(event.get('email'))
                        if email_filter == "With Email" and not has_email:
                            continue
                        elif email_filter == "Without Email" and has_email:
                            continue
                    
                    filtered_events.append(event)
                
                display_search_results(filtered_events, "Advanced Search Results")
                
            except Exception as e:
                st.error(f"Advanced search failed: {str(e)}")
    
    # Search history and suggestions
    with st.expander("💡 Search Tips"):
        st.markdown("""
        **Quick Search Tips:**
        - Use keywords that appear in event titles or descriptions
        - Search is case-insensitive
        - Partial matches are supported
        
        **Advanced Search Tips:**
        - Combine multiple filters for precise results
        - Leave filters as "All" to include all values
        - Date and time ranges help narrow down results
        - Use status filters to find specific types of events
        
        **Example Searches:**
        - "meeting" - Find all meetings
        - "interview" - Find interview events
        - "daily" - Find recurring daily events
        - "email" - Find events with email reminders
        """)

def display_search_results(results, search_query):
    """Display search results in a formatted way"""
    st.subheader(f"🔍 Search Results for '{search_query}'")
    st.markdown(f"**Found {len(results)} event(s)**")
    
    if not results:
        st.info("No events found matching your search criteria.")
        return
    
    # Sort options
    col1, col2 = st.columns([1, 3])
    with col1:
        sort_by = st.selectbox("Sort by:", ["Start Time", "Title", "Status"])
    
    # Sort results
    if sort_by == "Start Time":
        results.sort(key=lambda x: x['start_time'])
    elif sort_by == "Title":
        results.sort(key=lambda x: x['title'].lower())
    elif sort_by == "Status":
        results.sort(key=lambda x: get_event_status(x))
    
    # Display results with robust inline edit/delete
    for event in results:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.markdown(f"**{event['title']}**")
                st.caption(event['description'])
                if event.get('recurrence'):
                    st.caption(f"🔄 Recurring: {event['recurrence']}")
                if event.get('email'):
                    st.caption("📧 Email reminders enabled")
            with col2:
                st.text(f"📅 {format_datetime(event['start_time'])}")
                st.text(f"⏰ {format_datetime(event['end_time'])}")
            with col3:
                status = get_event_status(event)
                st.markdown(status)
            with col4:
                pass  # Edit and Delete buttons removed as requested
            st.markdown("---")

    # Export results
    st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.08em;margin-bottom:0.5em;'>
  <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:6px;'><path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/><polyline points='7 10 12 15 17 10'/><line x1='12' y1='15' x2='12' y2='3'/></svg>
  Export Results
</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to CSV"):
            # Prepare data for CSV
            csv_data = []
            for event in results:
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
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export to JSON"):
            json_data = pd.DataFrame(results).to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    search_events_page() 