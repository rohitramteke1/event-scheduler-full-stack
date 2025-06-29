from app import create_app
from app.tasks.reminder_task import start_reminder_thread
import os

app = create_app()

if __name__ == "__main__":
    # NOTE: # Prevent the thread from running twice due to Flask reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_reminder_thread()

    app.run(debug=True)
