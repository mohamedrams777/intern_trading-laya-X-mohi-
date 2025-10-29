# realtime.py
from flask_socketio import SocketIO
from threading import Thread
import time

# Create a SocketIO instance
socketio = SocketIO(cors_allowed_origins="*")

def broadcast_news(news_list):
    """Broadcast news updates to all connected clients"""
    socketio.emit("news_update", {"news": news_list})

def start_scheduler(app):
    """Run background tasks periodically"""
    def job():
        while True:
            with app.app_context():
                print("Background job running...")
                # Example: refresh data or run predictions
            time.sleep(3600)  # every hour

    Thread(target=job, daemon=True).start()

