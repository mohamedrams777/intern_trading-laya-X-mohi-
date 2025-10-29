from threading import Thread
import time
from utils import fetch_data

def start_scheduler(app):
    def job():
        while True:
            with app.app_context():
                print("Background job running...")
                # Example: refresh data or run predictions
            time.sleep(3600)  # every hour

    Thread(target=job, daemon=True).start()
