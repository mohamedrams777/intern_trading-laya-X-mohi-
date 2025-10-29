from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager # <-- NEW: Import LoginManager
from config import Config
from models import db, User # <-- Ensure User model is imported for user_loader
from routes import routes_bp
from realtime import socketio
from scheduler import start_scheduler
from extra_routes import extra_bp
from market_snapshot import market_bp, socketio, start_market_thread


login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/*": {"origins": "*"}})
   
    app.secret_key = 'temporary_insecure_key' 

    
    login_manager.init_app(app)

   
    @login_manager.user_loader
    def load_user(user_id):
       
        return db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
        
   
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"message": "Authorization Required. Please log in."}), 401


    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(routes_bp)
    app.register_blueprint(extra_bp)
    app.register_blueprint(market_bp) 
    socketio.init_app(app, cors_allowed_origins="*")

    start_market_thread()
    return app

if __name__ == "__main__":
    app = create_app()
    start_scheduler(app)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)