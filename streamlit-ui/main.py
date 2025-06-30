import streamlit as st
import time
from dotenv import load_dotenv
import os

# Set Streamlit theme (for Streamlit Cloud and local)
st.set_page_config(
    page_title="Event Scheduler",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
from datetime import datetime

# Add current directory to path to import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.api_client import EventAPIClient

# Load environment variables
load_dotenv()  # take environment variables from .env
API_DOCUMENTATION_URL = os.getenv("API_DOCUMENTATION_URL", "http://localhost:5000/apidocs")

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
    /* .stApp { padding-top: 70px; } removed */
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
    /* --- Improved dark mode override for Key Features cards --- */
    body[data-theme='dark'] .key-features-outer-card .feature-card {
        background: #232526 !important;
        border-color: #2c2f34 !important;
    }
    body[data-theme='dark'] .key-features-outer-card .feature-card-title,
    body[data-theme='dark'] .key-features-outer-card .feature-card ul,
    body[data-theme='dark'] .key-features-outer-card .feature-card li {
        color: #fff !important;
    }
    .section-card, .feature-card, .event-card, .events-list-card, .key-features-outer-card {
        color: var(--color-text);
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
    "Search Events": "<span style='font-size:1.1rem;'>🔍 Search Events</span>",
    "API Reference": "<span style='font-size:1.1rem;'>📖 API Reference</span>"
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

# --- Custom API Status Bar ---
# Modern floating API status dot with SVG icon, colored background, border radius, and fancy hover effect
api_status = st.session_state.get('api_status', None)
if api_status is None:
    api_status_color = "#f7b731"  # yellow/ochre for connecting
    api_status_text = "Connecting to API..."
    api_status_icon = """
        <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' style='display:block;'><path d='M12 2v20M2 12h20'/></svg>
    """  # plus/plug icon
elif api_status:
    api_status_color = "#43e97b"  # green for connected
    api_status_text = "API Connected"
    api_status_icon = """
        <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' style='display:block;'><polyline points='20 6 9 17 4 12'/></svg>
    """  # checkmark
else:
    api_status_color = "#ff6a6a"  # red for disconnected
    api_status_text = "API Disconnected"
    api_status_icon = """
        <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' style='display:block;'><line x1='18' y1='6' x2='6' y2='18'/><line x1='6' y1='6' x2='18' y2='18'/></svg>
    """  # x/cross

st.markdown(
    f"""
    <style>
    .api-status-fab {{
        position: fixed;
        bottom: 32px;
        right: 32px;
        z-index: 99999;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        pointer-events: auto;
    }}
    .api-status-dot {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: {api_status_color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        position: relative;
        transition: box-shadow 0.2s, transform 0.2s;
    }}
    .api-status-dot:hover {{
        box-shadow: 0 0 0 6px {api_status_color}55, 0 2px 16px rgba(0,0,0,0.18);
        transform: scale(1.10);
    }}
    .api-status-tooltip {{
        visibility: hidden;
        opacity: 0;
        width: max-content;
        background: #232526;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 7px 16px;
        position: absolute;
        bottom: 46px;
        right: 0;
        z-index: 100000;
        font-size: 1.02rem;
        font-weight: 500;
        transition: opacity 0.2s;
        pointer-events: none;
        white-space: nowrap;
        box-shadow: 0 2px 8px rgba(0,0,0,0.18);
    }}
    .api-status-dot:hover .api-status-tooltip {{
        visibility: visible;
        opacity: 1;
    }}
    </style>
    <div class="api-status-fab">
        <div class="api-status-dot">{api_status_icon}<span class="api-status-tooltip">{api_status_text}</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Now do the API status check/rerun logic as before
if 'api_status_checked' not in st.session_state:
    st.session_state['api_status_checked'] = False
    st.session_state['api_status'] = None
    st.session_state['api_status_text'] = 'Connecting'
    st.session_state['api_status_color'] = '#f7b731'  # yellow

# Show animated 'Connecting...' bar while checking
if not st.session_state['api_status_checked']:
    dots = '.' * int((time.time() * 2) % 4)
    st.markdown(
        f"""
<div style='width:100%;background:#f7b731;color:#18191A;font-weight:bold;text-align:center;padding:7px 0 5px 0;z-index:9999;font-size:1.1rem;display:flex;align-items:center;justify-content:center;'>
    <span style='display:inline-block;vertical-align:middle;margin-right:10px;'>
        <svg width='22' height='22' viewBox='0 0 50 50' style='animation:spin 1s linear infinite;'>
          <circle cx='25' cy='25' r='20' fill='none' stroke='#232526' stroke-width='5' opacity='0.2'/>
          <path d='M25 5a20 20 0 0 1 0 40' fill='none' stroke='#232526' stroke-width='5' stroke-linecap='round'/>
        </svg>
    </span>
    <span>Connecting{dots}...</span>
</div>
<style>@keyframes spin {{ from {{ transform: rotate(0deg);}} to {{ transform: rotate(360deg);}} }}</style>
        """,
        unsafe_allow_html=True
    )
    # Try API connection (only once per rerun)
    try:
        api_client = EventAPIClient()
        api_client.get_all_events()
        st.session_state['api_status'] = True
        st.session_state['api_status_text'] = '🟢 API Connected'
        st.session_state['api_status_color'] = '#43e97b'
    except Exception:
        st.session_state['api_status'] = False
        st.session_state['api_status_text'] = '🔴 API Disconnected'
        st.session_state['api_status_color'] = '#ff6a6a'
    st.session_state['api_status_checked'] = True
    st.rerun()

# Add Developer & API Info expander to sidebar
with st.sidebar.expander("⚙️ Developer & API Info", expanded=False):
    st.markdown(f'''
    <div style='font-weight:bold;display:flex;align-items:center;margin-bottom:8px;'>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFD600" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;">
        <path d="M12 2v20M2 12h20"/>
      </svg>
      API Status: <span style='color:#00D26A;font-weight:bold;margin-left:6px;'>●</span> API Connected
    </div>
    <div style='margin-bottom:6px;'>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 2v4"/><path d="M16 2v4"/></svg>
      <a href="{API_DOCUMENTATION_URL}" style="color:#00B4D8;text-decoration:underline;">Swagger UI</a>
    </div>
    <div style='margin-bottom:6px;font-weight:bold;'>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;">
        <circle cx="12" cy="7" r="4"/>
        <path d="M5.5 21a8.38 8.38 0 0 1 13 0"/>
      </svg>
      Developer: Rohit Ramteke
    </div>
    <div style='margin-bottom:2px;font-weight:bold;'>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;">
        <rect x="3" y="5" width="18" height="14" rx="2"/>
        <polyline points="3 7 12 13 21 7"/>
      </svg>
      Email: <a href="mailto:ramteker284@gmail.com" style="color:#00B4D8;text-decoration:underline;">ramteker284@gmail.com</a>
    </div>
    ''', unsafe_allow_html=True)

# --- Modern Custom Header/Banner (move to very top) ---
st.markdown('''
<style>
.custom-app-header {
    width: 100vw;
    max-width: 100vw;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 0.7rem 2.5vw 0.7rem 2.5vw;
    box-shadow: 0 2px 12px rgba(0,180,216,0.04);
    position: relative;
    z-index: 100;
    margin-bottom: 0.5rem;
}
body[data-theme="dark"] .custom-app-header {
    box-shadow: 0 2px 12px rgba(0,180,216,0.10);
}
.custom-app-header-logo {
    width: 38px;
    height: 38px;
    margin-right: 1.1rem;
    display: flex;
    align-items: center;
}
.custom-app-header-title {
    font-size: 2.1rem;
    font-weight: bold;
    color: #00B4D8;
    letter-spacing: 1px;
    margin-right: 2rem;
}
.custom-app-header-actions {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.stApp {
    padding: 0 !important;
    margin: 0 !important;
}
.block-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 2rem 2.5vw !important;
    width: 100% !important;
}
</style>
<div class="custom-app-header">
  <span class="custom-app-header-logo">
    <svg viewBox="0 0 32 32" width="38" height="38"><circle cx="16" cy="16" r="15" fill="#00B4D8"/><text x="16" y="22" text-anchor="middle" font-size="15" fill="#18191A" font-family="Arial" font-weight="bold">ES</text></svg>
  </span>
  <span class="custom-app-header-title">Event Scheduler</span>
  <span class="custom-app-header-actions">
    <!-- Future quick actions or user info can go here -->
  </span>
</div>
''', unsafe_allow_html=True)

# Page routing
page = st.session_state["nav_page"]
if page == "Home":
    def home_page(api_status):
        # --- Fetch event data and stats for Home page ---
        all_events = []
        total_events = 0
        upcoming_events = 0
        today_events = 0
        if api_status:
            try:
                api_client = EventAPIClient()
                all_events = api_client.get_all_events()
                total_events = len(all_events)
                upcoming_events = len([e for e in all_events if is_upcoming(e)])
                today_events = len([e for e in all_events if is_today(e)])
            except Exception as e:
                st.error(f"Failed to load statistics: {str(e)}")
        # --- Modern Welcome, Quick Overview, and Today's Events Cards ---
        st.markdown(f"""
<style>
.section-card, .events-list-card, .key-features-outer-card, .feature-card, .event-card {{
  /* No custom background or color: use Streamlit default */
  border-radius: 18px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
  padding: 2.2rem 2.5rem 1.7rem 2.5rem;
  margin-bottom: 2.2rem;
  border: 1.5px solid #e3f6fc;
  transition: box-shadow 0.18s, transform 0.18s;
}}
.section-card:hover {{
  box-shadow: 0 6px 32px rgba(0,180,216,0.13), 0 2px 16px rgba(0,0,0,0.10);
  transform: translateY(-2px) scale(1.012);
  border-color: #00B4D8;
}}
.section-heading, .subsection-heading, .feature-card-title, .event-title {{
  display: flex;
  align-items: center;
  font-size: 2.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  letter-spacing: 1px;
}}
.section-heading svg, .subsection-heading svg, .feature-card-title svg {{
  margin-right: 10px;
}}
.events-list-card {{
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,180,216,0.07);
  padding: 1.5rem 2rem 1.2rem 2rem;
  margin-bottom: 2.2rem;
  border: 1.2px solid #e3f6fc;
}}
.key-features-outer-card {{
  border-radius: 18px;
  box-shadow: 0 2px 16px rgba(0,180,216,0.10);
  padding: 2.2rem 2.5rem 2.2rem 2.5rem;
  margin-bottom: 2.2rem;
  border: 1.5px solid #e3f6fc;
}}
.feature-card-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2.2rem 2.5rem;
  margin-bottom: 0.5rem;
}}
.feature-card {{
  border-radius: 14px;
  box-shadow: 0 1px 6px rgba(0,180,216,0.04);
  padding: 1.3rem 1.5rem 1.1rem 1.5rem;
  transition: box-shadow 0.18s, transform 0.18s;
  border: 1.2px solid #e3f6fc;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}}
.feature-card:hover {{
  box-shadow: 0 4px 18px rgba(0,180,216,0.13), 0 2px 8px rgba(0,0,0,0.08);
  transform: translateY(-2px) scale(1.018);
  border-color: #00B4D8;
}}
.feature-card-title {{
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 1.13em;
  margin-bottom: 0.7rem;
}}
.feature-card-title svg {{
  margin-right: 10px;
}}
.feature-card ul {{
  margin: 0 0 0 1.1em;
  padding: 0;
}}
.event-card {{
  border-radius: 13px;
  box-shadow: 0 1px 6px rgba(0,180,216,0.04);
  padding: 1.1rem 1.5rem 1.1rem 1.5rem;
  margin-bottom: 1.1rem;
  border: 1.2px solid #e3f6fc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: box-shadow 0.18s, transform 0.18s;
}}
.event-card:hover {{
  box-shadow: 0 4px 18px rgba(0,180,216,0.13), 0 2px 8px rgba(0,0,0,0.08);
  transform: translateY(-1px) scale(1.012);
  border-color: #00B4D8;
}}
.event-info {{
  display: flex;
  flex-direction: column;
  justify-content: center;
}}
.event-title {{
  font-weight: 600;
  font-size: 1.08rem;
  margin-bottom: 2px;
}}
.event-desc {{
  font-size: 0.98rem;
}}
.event-time {{
  display: inline-flex;
  align-items: center;
  font-size: 1.05rem;
}}
.event-time svg {{
  margin-right: 6px;
  display: block;
  vertical-align: middle;
}}
</style>
<div class='section-card'>
  <div class='section-heading'>
    <svg width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
    Welcome to Event Scheduler!
  </div>
  <div style='color:#bdbdbd;font-size:1.08rem;margin-bottom:1.5rem;'>A powerful and intuitive event management system that helps you organize, schedule, and never miss important events. With features like email reminders, recurring events, and advanced search, managing your schedule has never been easier.</div>
  <div class='subsection-heading'>
    <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M3 18v-6a9 9 0 0 1 18 0v6'/><path d='M21 18a3 3 0 0 1-6 0'/><path d='M9 18a3 3 0 0 1-6 0'/></svg>
    Quick Overview
  </div>
  <div style='margin-bottom:2.2rem;'>
    <div style='display:flex;gap:3.5rem;'>
      <div>
        <div style='font-size:1.01rem;'>Total Events</div>
        <div style='font-size:2.2rem;font-weight:600;'>{total_events}</div>
      </div>
      <div>
        <div style='font-size:1.01rem;'>Upcoming</div>
        <div style='font-size:2.2rem;font-weight:600;'>{upcoming_events}</div>
      </div>
      <div>
        <div style='font-size:1.01rem;'>Today</div>
        <div style='font-size:2.2rem;font-weight:600;'>{today_events}</div>
      </div>
    </div>
  </div>
</div>
        """, unsafe_allow_html=True)
        # --- Today's Events List Card (heading and list together) ---
        st.markdown("""
<div class='events-list-card'>
  <div class='subsection-heading'>
    <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
    Today's Events
  </div>
  <div>
    <style>
      .event-card {
        border-radius: 13px;
        padding: 1.1rem 1.5rem 1.1rem 1.5rem;
        margin-bottom: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .event-info {
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
      .event-title {
        font-weight: 600;
        font-size: 1.08rem;
        margin-bottom: 2px;
      }
      .event-desc {
        font-size: 0.98rem;
      }
      .event-time {
        display: inline-flex;
        align-items: center;
        font-size: 1.05rem;
      }
      .event-time svg {
        margin-right: 6px;
        display: block;
        vertical-align: middle;
      }
    </style>
""", unsafe_allow_html=True)
        today_list = [e for e in all_events if is_today(e)]
        today_list.sort(key=lambda x: x['start_time'])
        for event in today_list[:3]:
            st.markdown(f"""
<div class='event-card'>
  <div class='event-info'>
    <span class='event-title'>{event['title']}</span>
    <span class='event-desc'>{event['description']}</span>
  </div>
  <div class='event-time'>
    <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='13' r='8'/><polyline points='12 9 12 13 15 15'/></svg>
    {format_time(event['start_time'])} - {format_time(event['end_time'])}
  </div>
</div>
            """, unsafe_allow_html=True)
        if len(today_list) > 3:
            st.caption(f"... and {len(today_list) - 3} more events today")
        st.markdown("""
  </div>
</div>
        """, unsafe_allow_html=True)
        # --- Render Key Features section inside a big card ---
        st.markdown("""
<div class='key-features-outer-card'>
  <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
    <span style="display: flex; align-items: center; margin-right: 10px;">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#00B4D8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
    </span>
    <span style="font-size:2.1rem;font-weight:bold;letter-spacing:1px;">Key Features</span>
  </div>
  <div class='feature-card-grid'>
    <div class='feature-card'>
      <div class='feature-card-title'>
        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
        Event Management
      </div>
      <ul>
        <li>Create, edit, and delete events</li>
        <li>Set start and end times</li>
        <li>Add descriptions and details</li>
      </ul>
    </div>
    <div class='feature-card'>
      <div class='feature-card-title'>
        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><path d='M12 6v6l4 2'/></svg>
        Recurring Events
      </div>
      <ul>
        <li>Daily, weekly, monthly recurrence</li>
        <li>Automatic future event creation</li>
        <li>Flexible scheduling options</li>
      </ul>
    </div>
    <div class='feature-card'>
      <div class='feature-card-title'>
        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='2' y='4' width='20' height='16' rx='2' ry='2'/><polyline points='22,6 12,13 2,6'/></svg>
        Email Reminders
      </div>
      <ul>
        <li>Automatic email notifications</li>
        <li>1-hour advance reminders</li>
        <li>Customizable email addresses</li>
      </ul>
    </div>
    <div class='feature-card'>
      <div class='feature-card-title'>
        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'/><line x1='21' y1='21' x2='16.65' y2='16.65'/></svg>
        Advanced Search
      </div>
      <ul>
        <li>Search by title or description</li>
        <li>Filter by date and time</li>
        <li>Status-based filtering</li>
      </ul>
    </div>
    <div class='feature-card'>
      <div class='feature-card-title'>
        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><line x1='9' y1='9' x2='15' y2='15'/><line x1='15' y1='9' x2='9' y2='15'/></svg>
        Analytics Dashboard
      </div>
      <ul>
        <li>Visual event statistics</li>
        <li>Timeline view</li>
        <li>Status distribution charts</li>
      </ul>
    </div>
    <div class='feature-card'>
      <div class='feature-card-title'>
        <svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#00B4D8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='2' y='7' width='20' height='14' rx='2' ry='2'/><path d='M16 3v4'/><path d='M8 3v4'/></svg>
        Responsive Design
      </div>
      <ul>
        <li>Works on desktop and mobile devices</li>
        <li>Clean, modern look</li>
      </ul>
    </div>
  </div>
</div>
        """, unsafe_allow_html=True)
    home_page(st.session_state['api_status'])
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
elif page == "API Reference":
    st.markdown(
        f'<iframe src="{API_DOCUMENTATION_URL}" width="100%" height="900"></iframe>',
        unsafe_allow_html=True
    ) 