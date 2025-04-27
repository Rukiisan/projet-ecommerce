from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from flask_apscheduler import APScheduler

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
scheduler = APScheduler()

def init_scheduler(app):
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()
        app.logger.info("Scheduler initialisé avec succès")

@socketio.on('join_auction')
def handle_join_auction(data):
    auction_id = data['auction_id']
    join_room(f'auction_{auction_id}')

@socketio.on('request_notifications')
def handle_notifications_request(data):
    customer_id = data['customer_id']  # Changé de user_id à customer_id
    unread = Notification.query.filter_by(customer_id=customer_id, is_read=False).all()
    emit('notifications_update', {
        'count': len(unread),
        'notifications': [n.to_dict() for n in unread]
    })