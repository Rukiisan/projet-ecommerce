from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    
    # Relations
    carts = db.relationship('Cart', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)
    bids = db.relationship('Bid', backref='customer', lazy=True)
    notifications = db.relationship('Notification', backref='customer', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000))
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    carts = db.relationship('Cart', backref='product', lazy=True)
    orders = db.relationship('Order', backref='product', lazy=True)
    auctions = db.relationship('Auction', backref='product', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_auction_win = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float)
    
    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), default='pending')
    payment_id = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# Modèles spécifiques aux enchères (à conserver)
class Auction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'anglaise', 'hollandaise', etc.
    start_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='open')
    price_step = db.Column(db.Float, default=10.0)  # Pour enchères hollandaises
    min_price = db.Column(db.Float, default=0.0)    # Pour enchères hollandaises
    decrement_interval = db.Column(db.Integer, default=5)  # Minutes entre décréments
    last_decrement = db.Column(db.DateTime)
    
    bids = db.relationship('Bid', backref='auction', lazy=True)
    cart_items = db.relationship('Cart', backref='auction', lazy=True)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'))