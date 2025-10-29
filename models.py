from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # The password will be stored as a hash for security
    password_hash = db.Column(db.String(255), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=True) # Optional field
    is_active = db.Column(db.Boolean, default=True) # Required by UserMixin

    def set_password(self, password):
        """Hashes the password and stores it in password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the plain text password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        # Required by UserMixin
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), nullable=False, index=True)
    side = db.Column(db.String(4), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(16), default="open")  # open / pending / executed / cancelled
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "price": self.price,
            "quantity": self.quantity,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

class PortfolioEntry(db.Model):
    __tablename__ = "portfolio"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), nullable=False, index=True)
    quantity = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {"id": self.id, "symbol": self.symbol, "quantity": self.quantity}

class SimulationResult(db.Model):
    __tablename__ = "simulations"
    id = db.Column(db.Integer, primary_key=True)
    start_price = db.Column(db.Float, nullable=False)
    simulations = db.Column(db.Integer, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    mean_final = db.Column(db.Float)
    median_final = db.Column(db.Float)
    pct5 = db.Column(db.Float)
    pct95 = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "start_price": self.start_price,
            "simulations": self.simulations,
            "days": self.days,
            "mean_final": self.mean_final,
            "median_final": self.median_final,
            "5pct": self.pct5,
            "95pct": self.pct95,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Trade(db.Model):
    __tablename__ = "trades"
    id = db.Column(db.Integer, primary_key=True)
    buy_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "quantity": self.quantity,
            "timestamp": self.timestamp.isoformat(),
        }

def buy_or_hold(current_price, predicted_price):
    current_price = float(current_price)
    predicted_price = float(predicted_price)
    change = ((predicted_price - current_price) / current_price) * 100
    if change > 2:
        return "Buy 📈"
    else:
        return "Hold 🤝"