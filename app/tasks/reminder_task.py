import threading
import time
from datetime import datetime, timedelta
from app.services.event_service import get_all_events
from app.utils.email_utils import send_email

# Recurrence intervals
RECURRING_INTERVALS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),  # approx.
}

seen_reminders = set() 


def check_reminders():
    while True:
        try:
            now = datetime.now()
            upcoming = now + timedelta(hours=1)
            events = get_all_events()

            for event in events:
                start_time = datetime.fromisoformat(event["start_time"])
                recurrence = event.get("recurrence")

                # Skip past non-recurring events
                if recurrence is None and start_time < now:
                    continue

                # For recurring events, move to next valid future occurrence
                if recurrence in RECURRING_INTERVALS:
                    while start_time < now:
                        start_time += RECURRING_INTERVALS[recurrence]

                # Reminder check
                if now <= start_time <= upcoming:
                    reminder_key = f"{event['id']}_{start_time.isoformat()}"
                    if reminder_key not in seen_reminders:
                        print(f"🔔 Reminder: '{event['title']}' is starting at {start_time.strftime('%Y-%m-%d %H:%M')}")
                        seen_reminders.add(reminder_key)

                        # ✅ Email support
                        if event.get("email"):
                            subject = f"Reminder: {event['title']} is starting soon"
                            body = (
                                f"⏰ Event: {event['title']}\n"
                                f"📅 Time: {start_time.strftime('%Y-%m-%d %H:%M')}\n"
                                f"📝 Description: {event['description']}"
                            )
                            send_email(event["email"], subject, body)

        except Exception as e:
            print("⚠️ Reminder check error:", e)

        time.sleep(60)


def start_reminder_thread():
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()
