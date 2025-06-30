import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
            return "upcoming"
        elif start_time <= now <= end_time:
            return "ongoing"
        else:
            return "past"
    except:
        return "unknown"

def create_dashboard():
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
    <svg width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><path d='M9 17v-6h6v6'/></svg>
  </span><span style='font-size:2.1rem;font-weight:bold;letter-spacing:1px;'>Event Scheduler Dashboard</span>
</h2>
    """, unsafe_allow_html=True)

    # --- Move Quick Actions to top ---
    st.markdown("""
<div class='section-heading'>
  <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='13 2 13 9 20 9'/><path d='M20 9a8.1 8.1 0 0 1-15.5 4'/></svg>
  Quick Actions
</div>
""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Create New Event", key="create_event_btn", type="primary", help="Create a new event", use_container_width=True):
            st.session_state["nav_page"] = "Create Event"
            st.rerun()
    with col2:
        if st.button("View All Events", key="view_events_btn", use_container_width=True):
            st.session_state["nav_page"] = "View Events"
            st.rerun()
    with col3:
        if st.button("Search Events", key="search_events_btn", use_container_width=True):
            st.session_state["nav_page"] = "Search Events"
            st.rerun()

    st.markdown("---")
    
    # Initialize API client
    try:
        api_client = EventAPIClient()
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")
        return
    
    try:
        # Get all events
        all_events = api_client.get_all_events()
        
        if not all_events:
            st.info("No events found. Create your first event to see the dashboard!")
            return
        
        # Calculate statistics
        total_events = len(all_events)
        upcoming_events = len([e for e in all_events if get_event_status(e) == "upcoming"])
        ongoing_events = len([e for e in all_events if get_event_status(e) == "ongoing"])
        past_events = len([e for e in all_events if get_event_status(e) == "past"])
        
        recurring_events = len([e for e in all_events if e.get('recurrence')])
        events_with_email = len([e for e in all_events if e.get('email')])
        
        # Display key metrics
        st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.25em;margin-bottom:0.5em;'>
  <svg width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><line x1='9' y1='17' x2='9' y2='13'/><line x1='15' y1='17' x2='15' y2='9'/></svg>
  Key Metrics
</div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", total_events)
        
        with col2:
            st.metric("Upcoming", upcoming_events, delta=upcoming_events)
        
        with col3:
            st.metric("Ongoing", ongoing_events)
        
        with col4:
            st.metric("Past Events", past_events)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Recurring Events", recurring_events)
        
        with col2:
            st.metric("Events with Email", events_with_email)
        
        st.markdown("---")
        
        # Event Status Distribution Chart
        st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><circle cx='12' cy='12' r='10'/><path d='M2 12h20'/><path d='M12 2a10 10 0 0 1 10 10'/></svg>
  Event Status Distribution
</div>
        """, unsafe_allow_html=True)
        
        status_data = {
            'Status': ['Upcoming', 'Ongoing', 'Past'],
            'Count': [upcoming_events, ongoing_events, past_events],
        }
        
        fig_pie = px.pie(
            values=status_data['Count'],
            names=status_data['Status'],
            title="Events by Status",
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Events Timeline
        st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
  Events Timeline (Next 30 Days)
</div>
        """, unsafe_allow_html=True)
        
        # Filter events for next 30 days
        now = datetime.now()
        future_date = now + timedelta(days=30)
        
        timeline_events = []
        for event in all_events:
            try:
                start_time = datetime.fromisoformat(event['start_time'])
                if start_time >= now and start_time <= future_date:
                    timeline_events.append({
                        'title': event['title'],
                        'start_time': start_time,
                        'status': get_event_status(event),
                        'recurrence': event.get('recurrence', 'None')
                    })
            except:
                continue
        
        if timeline_events:
            # Sort by start time
            timeline_events.sort(key=lambda x: x['start_time'])
            
            # Create timeline chart
            fig_timeline = go.Figure()
            
            for event in timeline_events:
                color_map = {
                    'upcoming': '#00ff00',
                    'ongoing': '#ffff00',
                    'past': '#ff0000'
                }
                
                fig_timeline.add_trace(go.Scatter(
                    x=[event['start_time']],
                    y=[event['title']],
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color=color_map.get(event['status'], '#888888'),
                        symbol='circle'
                    ),
                    text=[event['title']],
                    textposition="middle right",
                    name=event['title'],
                    hovertemplate=f"<b>{event['title']}</b><br>" +
                                f"Time: {event['start_time'].strftime('%Y-%m-%d %H:%M')}<br>" +
                                f"Status: {event['status']}<br>" +
                                f"Recurrence: {event['recurrence']}<extra></extra>"
                ))
            
            fig_timeline.update_layout(
                title="Events Timeline",
                xaxis_title="Date & Time",
                yaxis_title="Events",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No upcoming events in the next 30 days.")
        
        # Upcoming Events List
        st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>
  Upcoming Events
</div>
        """, unsafe_allow_html=True)
        
        upcoming_list = []
        for event in all_events:
            status = get_event_status(event)
            if status == "upcoming":
                upcoming_list.append(event)
        
        # Sort by start time and take top 5
        upcoming_list.sort(key=lambda x: x['start_time'])
        upcoming_list = upcoming_list[:5]
        
        if upcoming_list:
            # --- Modern Carded Table UI for Events ---
            st.markdown('''
<style>
.event-table-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.9rem 1.2rem 0.9rem 1.2rem;
  font-weight: bold;
  font-size: 1.09rem;
  border-radius: 13px;
  margin-bottom: 1.1rem;
  border: 1.2px solid #00B4D8;
}
.event-card-row {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  padding: 1.2rem 1.2rem 1.1rem 1.2rem;
  border-radius: 13px;
  box-shadow: 0 2px 12px rgba(0,180,216,0.07);
  margin-bottom: 1.2rem;
  border: 1.2px solid #22283122;
  transition: box-shadow 0.18s, transform 0.18s;
}
.event-card-row:hover {
  box-shadow: 0 6px 24px rgba(0,180,216,0.13), 0 2px 16px rgba(0,0,0,0.10);
  transform: translateY(-2px) scale(1.012);
  border-color: #00B4D8;
}
.event-card-cell {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 1.04rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.event-card-title {
  font-weight: 600;
  font-size: 1.08rem;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.event-card-desc {
  color: #bdbdbd;
  font-size: 0.98rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
@media (max-width: 900px) {
  .event-table-header, .event-card-row {
    flex-direction: column;
    gap: 0.7rem;
    padding: 1.1rem 0.7rem;
  }
  .event-card-cell {
    width: 100%;
    justify-content: flex-start;
  }
}
body[data-theme="dark"] .event-table-header {
  border-color: #00B4D8;
}
body[data-theme="dark"] .event-card-row {
  border-color: #22283155;
}
</style>
''', unsafe_allow_html=True)

            # Table header
            st.markdown("""
<div class='event-table-header'>
  <div style='flex:2;'>Event</div>
  <div style='flex:1;'>Start Time</div>
  <div style='flex:1;'>End Time</div>
  <div style='flex:1;'>Recurrence</div>
  <div style='flex:1;'>Email</div>
</div>
""", unsafe_allow_html=True)

            for event in upcoming_list:
                st.markdown(f"""
<div class='event-card-row'>
  <div style='flex:2;min-width:0;display:flex;flex-direction:column;'>
    <span class='event-card-title'>{event['title']}</span>
    <span class='event-card-desc'>{event['description']}</span>
  </div>
  <div class='event-card-cell'>
    <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/></svg>
    {format_datetime(event['start_time'])}
  </div>
  <div class='event-card-cell'>
    <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='13' r='8'/><polyline points='12 9 12 13 15 15'/></svg>
    {format_datetime(event['end_time'])}
  </div>
  <div class='event-card-cell'>
    {('<svg width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'#00B4D8\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><circle cx=\'12\' cy=\'12\' r=\'10\'/><path d=\'M12 6v6l4 2\'/></svg>' + str(event['recurrence'])) if event.get('recurrence') else ''}
  </div>
  <div class='event-card-cell'>
    {('<svg width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'#00B4D8\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><rect x=\'2\' y=\'7\' width=\'20\' height=\'14\' rx=\'2\' ry=\'2\'/><path d=\'M16 3v4\'/><path d=\'M8 3v4\'/></svg> Reminder enabled') if event.get('email') else ''}
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.info("No upcoming events.")
        
        # Recent Events
        st.markdown("""
<div style='display:flex;align-items:center;font-weight:bold;font-size:1.15em;margin-bottom:0.5em;'>
  <svg width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='margin-right:8px;'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='9' y1='9' x2='15' y2='9'/><line x1='9' y1='13' x2='15' y2='13'/><line x1='9' y1='17' x2='15' y2='17'/></svg>
  Recent Events
</div>
        """, unsafe_allow_html=True)
        
        recent_events = []
        for event in all_events:
            status = get_event_status(event)
            if status == "past":
                recent_events.append(event)
        
        # Sort by start time (most recent first) and take top 5
        recent_events.sort(key=lambda x: x['start_time'], reverse=True)
        recent_events = recent_events[:5]
        
        if recent_events:
            # --- Blue separator line before Recent Events with extra space above ---
            st.markdown("<div style='margin-top:2.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='height:2px;background:#00B4D8;margin:0 0 1.2rem 0;'></div>", unsafe_allow_html=True)

            # Table header for Recent Events
            st.markdown("""
<div class='event-table-header'>
  <div style='flex:2;'>Event</div>
  <div style='flex:1;'>Start Time</div>
  <div style='flex:1;'>End Time</div>
  <div style='flex:1;'>Recurrence</div>
  <div style='flex:1;'>Email</div>
</div>
""", unsafe_allow_html=True)

            for event in recent_events:
                st.markdown(f"""
<div class='event-card-row'>
  <div style='flex:2;min-width:0;display:flex;flex-direction:column;'>
    <span class='event-card-title'>{event['title']}</span>
    <span class='event-card-desc'>{event['description']}</span>
  </div>
  <div class='event-card-cell'>
    <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/></svg>
    {format_datetime(event['start_time'])}
  </div>
  <div class='event-card-cell'>
    <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='13' r='8'/><polyline points='12 9 12 13 15 15'/></svg>
    {format_datetime(event['end_time'])}
  </div>
  <div class='event-card-cell'>
    {('<svg width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'#00B4D8\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><circle cx=\'12\' cy=\'12\' r=\'10\'/><path d=\'M12 6v6l4 2\'/></svg>' + str(event['recurrence'])) if event.get('recurrence') else ''}
  </div>
  <div class='event-card-cell'>
    {('<svg width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'#00B4D8\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><rect x=\'2\' y=\'7\' width=\'20\' height=\'14\' rx=\'2\' ry=\'2\'/><path d=\'M16 3v4\'/><path d=\'M8 3v4\'/></svg> Reminder enabled') if event.get('email') else ''}
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.info("No recent events.")
        
    except Exception as e:
        st.error(f"Failed to load dashboard data: {str(e)}")

if __name__ == "__main__":
    create_dashboard() 