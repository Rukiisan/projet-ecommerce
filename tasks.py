from extensions import scheduler, socketio, db
from models import Auction
from datetime import datetime, timedelta
from sqlalchemy import or_
import logging

logger = logging.getLogger(__name__)

def init_dutch_auction_task(app):
    @scheduler.task('interval', id='dutch_auction_decrement', seconds=30)
    def decrement_dutch_auctions():
        with app.app_context():
            try:
                now = datetime.utcnow()
                logger.info(f"Début décrément à {now}")
                
                auctions = Auction.query.filter(
                    Auction.type == 'hollandaise',
                    Auction.status == 'active',
                    Auction.current_price > Auction.min_price
                ).all()

                for auction in auctions:
                    new_price = max(auction.min_price, auction.current_price - auction.price_step)
                    auction.current_price = new_price
                    auction.last_decrement = now
                    
                    if new_price <= auction.min_price:
                        auction.status = 'closed'
                    
                    socketio.emit('price_update', {
                        'auction_id': auction.id,
                        'new_price': new_price
                    })
                
                db.session.commit()
            except Exception as e:
                logger.error(f"Erreur: {str(e)}")
                db.session.rollback()