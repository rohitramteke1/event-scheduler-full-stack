import streamlit as st

# Set Streamlit theme (for Streamlit Cloud and local)
st.set_page_config(
    page_title="Event Scheduler",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
import os
from datetime import datetime

# Add current directory to path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.api_client import EventAPIClient

# --- Utility functions (move above usage) ---
def is_upcoming(event):
    try:
        start = datetime.fromisoformat(event['start_time'])
        return start > datetime.now()
    except:
        return False

def is_today(event):
    try:
        start = datetime.fromisoformat(event['start_time'])
        now = datetime.now()
        return start.date() == now.date()
    except:
        return False

def format_time(dt_str):
    try:
        return datetime.fromisoformat(dt_str).strftime("%I:%M %p")
    except:
        return dt_str

# Remove forced dark theme CSS. Only keep custom sidebar and layout styles.
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        text-align: left;
        color: #00B4D8;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        margin-left: 1.5rem;
    }
    .topnav {
        background: #232526;
        display: flex;
        align-items: center;
        padding: 0.5rem 1.5rem;
        border-bottom: 1.5px solid #00B4D8;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        z-index: 1000;
        height: 60px;
    }
    .nav-link {
        color: #E4E6EB;
        text-decoration: none;
        margin: 0 1.2rem;
        font-size: 1.1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        transition: color 0.2s;
        border-bottom: 2px solid transparent;
        padding-bottom: 2px;
    }
    .nav-link.selected, .nav-link:hover {
        color: #00B4D8;
        border-bottom: 2px solid #00B4D8;
    }
    .nav-icon {
        width: 22px;
        height: 22px;
        margin-right: 0.5rem;
        vertical-align: middle;
        fill: currentColor;
    }
    .nav-spacer { flex: 1; }
    .api-status {
        font-size: 0.95rem;
        margin-left: 1.5rem;
        color: #43e97b;
        font-weight: 600;
    }
    .api-status.error { color: #ff6a6a; }
    .stApp { padding-top: 70px; }
    /* Sidebar custom styles */
    .sidebar-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        margin-top: 1rem;
        margin-left: 0.5rem;
    }
    .sidebar-logo {
        width: 32px;
        height: 32px;
        margin-right: 0.7rem;
    }
    .sidebar-title {
        color: #00B4D8;
        font-size: 1.4rem;
        font-weight: bold;
        letter-spacing: 1px;
    }
    /* Style the radio navigation */
    div[data-testid="stSidebar"] > div:first-child {
        padding-bottom: 0;
    }
    .css-1v0mbdj, .css-1v0mbdj > div { /* radio group container */
        background: none !important;
        box-shadow: none !important;
    }
    .css-1v0mbdj label, .css-1v0mbdj span {
        font-size: 1.08rem !important;
        font-weight: 500 !important;
        color: inherit !important;
        padding: 0.6rem 1rem !important;
        border-radius: 8px !important;
        margin-bottom: 0.2rem !important;
        transition: background 0.2s, color 0.2s;
    }
    .css-1v0mbdj label[data-selected="true"], .css-1v0mbdj label:hover {
        background: #232526 !important;
        color: #00B4D8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown("""
<div class='sidebar-header'>
    <svg class='sidebar-logo' viewBox='0 0 24 24'><circle cx='12' cy='12' r='10' fill='#00B4D8'/><text x='12' y='16' text-anchor='middle' font-size='12' fill='#18191A' font-family='Arial' font-weight='bold'>ES</text></svg>
    <span class='sidebar-title'>Event Scheduler</span>
</div>
""", unsafe_allow_html=True)

# Robust navigation: use session state as the single source of truth
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Home"

PAGES = {
    "Home": "<span style='font-size:1.1rem;'>🏠 Home</span>",
    "Dashboard": "<span style='font-size:1.1rem;'>4c8 Dashboard</span>",
    "Create Event": "<span style='font-size:1.1rem;'>➕ Create Event</span>",
    "View Events": "<span style='font-size:1.1rem;'>4c4 View Events</span>",
    "Search Events": "<span style='font-size:1.1rem;'>🔍 Search Events</span>"
}

selected = st.sidebar.radio(
    "Navigation",
    list(PAGES.keys()),
    index=list(PAGES.keys()).index(st.session_state["nav_page"]),
    format_func=lambda x: x,
    label_visibility="collapsed",
    key="sidebar_nav_radio"
)

if selected != st.session_state["nav_page"]:
    st.session_state["nav_page"] = selected
    st.rerun()

# API Status in top nav
try:
    api_client = EventAPIClient()
    api_client.get_all_events()
    api_status = True
    api_status_html = "<span class='api-status'>API Connected</span>"
except Exception as e:
    api_status = False
    api_status_html = "<span class='api-status error'>API Disconnected</span>"

nav_html = "<div class='topnav'>"
nav_html += "<span class='main-header'>Event Scheduler</span>"
nav_html += "<div class='nav-spacer'></div>"
nav_html += api_status_html
nav_html += "</div>"
st.markdown(nav_html, unsafe_allow_html=True)

# Page routing
page = st.session_state["nav_page"]
if page == "Home":
    def home_page(api_status):
        st.subheader("🎉 Welcome to Event Scheduler!")
        st.markdown("""
        <span style='color:#bdbdbd;'>A powerful and intuitive event management system that helps you organize, 
schedule, and never miss important events. With features like email reminders, 
recurring events, and advanced search, managing your schedule has never been easier.</span>
        """, unsafe_allow_html=True)
        # Quick stats (if API is connected)
        if api_status:
            try:
                api_client = EventAPIClient()
                all_events = api_client.get_all_events()
                # Calculate quick stats
                total_events = len(all_events)
                upcoming_events = len([e for e in all_events if is_upcoming(e)])
                today_events = len([e for e in all_events if is_today(e)])
                st.subheader("📈 Quick Overview")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Total Events", total_events)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Upcoming", upcoming_events)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Today", today_events)
                    st.markdown('</div>', unsafe_allow_html=True)
                # Show today's events
                if today_events > 0:
                    st.subheader("📅 Today's Events")
                    today_list = [e for e in all_events if is_today(e)]
                    today_list.sort(key=lambda x: x['start_time'])
                    for event in today_list[:3]:  # Show first 3
                        with st.container():
                            col1, col2, col3 = st.columns([3, 2, 1])
                            with col1:
                                st.markdown(f"**{event['title']}**")
                                st.caption(event['description'])
                            with col2:
                                start_time = format_time(event['start_time'])
                                end_time = format_time(event['end_time'])
                                st.text(f"⏰ {start_time} - {end_time}")
                            with col3:
                                if event.get('email'):
                                    st.caption("📧 Reminders")
                            st.markdown("---")
                    if len(today_list) > 3:
                        st.caption(f"... and {len(today_list) - 3} more events today")
            except Exception as e:
                st.error(f"Failed to load statistics: {str(e)}")
        # Features section
        st.subheader("✨ Key Features")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("**📅 Event Management**")
            st.markdown("- Create, edit, and delete events")
            st.markdown("- Set start and end times")
            st.markdown("- Add descriptions and details")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("**🔄 Recurring Events**")
            st.markdown("- Daily, weekly, monthly recurrence")
            st.markdown("- Automatic future event creation")
            st.markdown("- Flexible scheduling options")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("**📧 Email Reminders**")
            st.markdown("- Automatic email notifications")
            st.markdown("- 1-hour advance reminders")
            st.markdown("- Customizable email addresses")
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("**🔍 Advanced Search**")
            st.markdown("- Search by title or description")
            st.markdown("- Filter by date and time")
            st.markdown("- Status-based filtering")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("**📊 Analytics Dashboard**")
            st.markdown("- Visual event statistics")
            st.markdown("- Timeline view")
            st.markdown("- Status distribution charts")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("**📱 Responsive Design**")
            st.markdown("- Works on desktop and mobile devices")
            st.markdown("- Clean, modern look")
            st.markdown("</div>", unsafe_allow_html=True)
    home_page(api_status)
elif page == "Dashboard":
    from _pages.dashboard import create_dashboard
    create_dashboard()
elif page == "Create Event":
    from _pages.create_event import create_event_page
    create_event_page()
elif page == "View Events":
    from _pages.view_events import view_events_page
    view_events_page()
elif page == "Search Events":
    from _pages.search_events import search_events_page
    search_events_page() 