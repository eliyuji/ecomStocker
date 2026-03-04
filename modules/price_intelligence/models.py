from sqlalchemy import Column, Integer, String, Float, DateTime, Numeric, Text, JSON, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from config.database import Base

# Price check model --> One row per scape job for a specific product

class PriceCheck(Base):
    __tablename__ = 'price_checks'
    
    check_id = Column(Integer, primary_key = True, index = True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable = False)
    source = Column(String(50), nullable = False)
    average_price = Column(Numeric(10, 2))
    min_price = Column(Numeric(10, 2))
    max_price = Column(Numeric(10, 2))
    sample_size = Column(Integer)
    confidence = Column(String(20))
    raw_data = Column(JSON)
    checked_at = Column(DateTime)

    product = relationship("Product")

    def to_dict(self):
        return {
            'check_id': self.check_id,
            'product_id': self.product_id,
            'source': self.source,
            'average_price': float(self.average_price) if self.average_price is not None else None,
            'min_price': float(self.min_price) if self.min_price is not None else None,
            'max_price': float(self.max_price) if self.max_price is not None else None,
            'sample_size': self.sample_size,
            'confidence': self.confidence,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None
        }
    
    def __repr__(self):
        return f"<PriceCheck(product={self.product_id}, source={self.source}, avg={self.average_price})>"

#Market Sale Model
# One row per individual sold listing found during scraping
#For analyzer use

class MarketSale(Base):
    __tablename__ = 'market_sales'

    sale_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100))
    condition = Column(String(50))
    sold_price = Column(Numeric(10, 2), nullable=False)
    sold_date = Column(Date)
    source = Column(String(50))
    source_url = Column(String(500))
    created_at = Column(DateTime)

    def to_dict(self):
        return {
            'sale_id': self.sale_id,
            'product_name': self.product_name,
            'category' : self.category,
            'condition': self.condition,
            'sold__price': float(self.sold_price) if self.sold_price else None,
            'sold_date': self.sold_date.isoformat() if self.sold_date else None,
            'source': self.source,
            'source_url': self.source_url,
        }
    def __repr__(self):
        return f"<MarketSale(product={self.product_name}, price={self.sold_price}, date={self.sold_date})>"
    
class PriceAlert(Base):
    #alert_id SERIAL PRIMARY KEY,
    #user_id INT NOT NULL REFERENCES users(user_id),
    #product_id INT NOT NULL REFERENCES products(product_id)
    #alert_type VARCHAR(50) NOT NULL, -- e.g. "below", "above", "percentage_drop"
    #target_price DECIMAL(10,2)
    #percentage_drop INT,
    #is_active BOOLEAN DEFAULT TRUE,
    #created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #last_triggered_at TIMESTAMP
    __tablename__ = 'price_alerts'
    alert_id = Column(Integer, primary_key= True, index = True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    alert_type = Column(String(50), nullable=False)
    target_price = Column(Numeric(10,2))
    percentage_drop = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    last_triggered_at = Column(DateTime)

    user = relationship("User")
    product = relationship('Product')
    notification = relationship('AlertNotification', back_populates='alert', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'alert_type': self.alert_type,
            'target_price': float(self.target_price) if self.target_price else None,
            'percentage_drop': self.percentage_drop,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None
        }
    def __repr__(self):
        return f"<PriceAlert(user_id={self.user_id}, product_id={self.product_id}, type={self.alert_type})>"

class AlertNotification(Base):
    __tablename__ = 'alert__notifications'

    notification_id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey('price_alerts.alert_id'), nullable=False)
    old_price = Column(Numeric(10,2))
    new_price = Column(Numeric(10,2))
    notificiation_sent = Column(Boolean, default=False)
    notification_method = Column(String(50))
    triggered_at = Column(DateTime)

    alert = relationship('PriceAlert', back_populates='notification')
    
    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'alert_id': self.alert_id,
            'old_price': float(self.old_price) if self.old_price else None,
            'new_price': float(self.new_price) if self.new_price else None,
            'notificiation_sent': self.notificiation_sent,
            'notification_method': self.notification_method,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None
        }
    def __repr__(self):
        return f"<AlertNotification(alert_id={self.alert_id}, old_price={self.old_price}, new_price={self.new_price})>"