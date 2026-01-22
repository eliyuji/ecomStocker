"""
Product model and schemas
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    brand = Column(String(100))
    stock_quantity = Column(Integer, default=0)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    interactions = relationship("UserProductInteraction", back_populates="product", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': float(self.price) if self.price else None,
            'description': self.description,
            'brand': self.brand,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f"<Product(id={self.product_id}, name='{self.name}', price={self.price})>"