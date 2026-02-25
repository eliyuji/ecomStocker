from sqlalchemy import Column, Integer, String, Float, DateTime, Numeric, Text, JSON, Boolean
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
