from flask import Flask
from flask_cors import CORS
from extensions import db, socketio, scheduler
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from models import Customer

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SCHEDULER_API_ENABLED'] = True

    # Initialisation des extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    socketio.init_app(app)
    CORS(app)

    # Authentification
    login_manager = LoginManager(app)
    login_manager.login_view = "customer_bp.login_api"

    @login_manager.user_loader
    def load_user(user_id):
        return Customer.query.get(int(user_id))

    # Enregistrement des blueprints
    from products import product_bp
    from customers import customer_bp
    from auctions import auction_bp

    app.register_blueprint(product_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(auction_bp, url_prefix='/api/auctions')

    # Initialisation de la base de données
    with app.app_context():
        db.create_all()

        # Création de l'admin si nécessaire
        if not Customer.query.filter_by(username='admin').first():
            admin = Customer(
                username='admin',
                email='admin@example.com',
                password='adminpassword',  # Le setter hash automatiquement
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin customer created")

    return app

app = create_app()

# Initialisation du scheduler
scheduler.init_app(app)
from tasks import init_dutch_auction_task
init_dutch_auction_task(app)

if __name__ == '__main__':
    socketio.run(app, debug=True)