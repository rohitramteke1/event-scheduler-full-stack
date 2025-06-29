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
    st.header("📊 Event Scheduler Dashboard")
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
        st.subheader("📈 Key Metrics")
        
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
        st.subheader("📊 Event Status Distribution")
        
        status_data = {
            'Status': ['Upcoming', 'Ongoing', 'Past'],
            'Count': [upcoming_events, ongoing_events, past_events],
            'Color': ['#00ff00', '#ffff00', '#ff0000']
        }
        
        fig_pie = px.pie(
            values=status_data['Count'],
            names=status_data['Status'],
            title="Events by Status",
            color_discrete_sequence=['#00ff00', '#ffff00', '#ff0000']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Events Timeline
        st.subheader("📅 Events Timeline (Next 30 Days)")
        
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
        st.subheader("⏰ Upcoming Events")
        
        upcoming_list = []
        for event in all_events:
            status = get_event_status(event)
            if status == "upcoming":
                upcoming_list.append(event)
        
        # Sort by start time and take top 5
        upcoming_list.sort(key=lambda x: x['start_time'])
        upcoming_list = upcoming_list[:5]
        
        if upcoming_list:
            for event in upcoming_list:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{event['title']}**")
                        st.caption(event['description'])
                        if event.get('recurrence'):
                            st.caption(f"🔄 Recurring: {event['recurrence']}")
                    
                    with col2:
                        st.text(f"📅 {format_datetime(event['start_time'])}")
                        st.text(f"⏰ {format_datetime(event['end_time'])}")
                    
                    with col3:
                        if event.get('email'):
                            st.caption("📧 Email reminders enabled")
                    
                    st.markdown("---")
        else:
            st.info("No upcoming events.")
        
        # Recent Events
        st.subheader("📋 Recent Events")
        
        recent_events = []
        for event in all_events:
            status = get_event_status(event)
            if status == "past":
                recent_events.append(event)
        
        # Sort by start time (most recent first) and take top 5
        recent_events.sort(key=lambda x: x['start_time'], reverse=True)
        recent_events = recent_events[:5]
        
        if recent_events:
            for event in recent_events:
                with st.container():
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        st.markdown(f"**{event['title']}**")
                        st.caption(event['description'])
                    
                    with col2:
                        st.text(f"📅 {format_datetime(event['start_time'])}")
                        st.text(f"⏰ {format_datetime(event['end_time'])}")
                    
                    st.markdown("---")
        else:
            st.info("No recent events.")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Create New Event", type="primary"):
                st.session_state["nav_page"] = "Create Event"
        
        with col2:
            if st.button("📋 View All Events"):
                st.session_state["nav_page"] = "View Events"
        
        with col3:
            if st.button("🔍 Search Events"):
                st.session_state["nav_page"] = "Search Events"
        
    except Exception as e:
        st.error(f"Failed to load dashboard data: {str(e)}")

if __name__ == "__main__":
    create_dashboard() 