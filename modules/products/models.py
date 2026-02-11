"""
Product model and schemas
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
from sqlalchemy import ForeignKey

VALID_CONDITIONS = ['mint', 'near_mint', 'excellent', 'good', 'fair', 'poor']
VALID_RARITIES   = ['common', 'uncommon', 'rare', 'ultra_rare']

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("trinket_categories.category_id"), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    brand = Column(String(100))
    stock_quantity = Column(Integer, default=1)  # Usually 1 for trinkets
    image_url = Column(String(500))
    
    condition = Column(String(50))  # "mint", "used", "vintage", "damaged"
    year_manufactured = Column(Integer)  # For vintage items
    brand = Column(String(100))
    material = Column(String(100))  # "ceramic", "metal", "plastic", etc.
    dimensions = Column(String(100))  # "5x3x2 inches"
    rarity = Column(String(50))  # "common", "uncommon", "rare"
    authenticity_verified = Column(Boolean, default=False)  # For collectibles

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Price intelligence fields
    suggested_price = Column(Numeric(10, 2))
    price_confidence = Column(String(20))  # "high", "medium", "low"
    market_average = Column(Numeric(10, 2))
    last_market_check = Column(DateTime)

    
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    interactions = relationship("UserProductInteraction", back_populates="product", cascade="all, delete-orphan")
    category = relationship("TrinketCategory")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'product_id':    self.product_id,
            'name':          self.name,
            'category_id': self.category_id,
            'price':         float(self.price) if self.price else None,
            'description':   self.description,
            'brand':         self.brand,
            'stock_quantity': self.stock_quantity,
            'image_url':     self.image_url,
            'created_at':    self.created_at.isoformat() if self.created_at else None,
            'is_active':     self.is_active,

            # New: trinket-specific
            'condition':              self.condition,
            'year_manufactured':      self.year_manufactured,
            'rarity':                 self.rarity,
            'material':               self.material,
            'dimensions':             self.dimensions,
            'authenticity_verified':  self.authenticity_verified,

            # New: price intelligence (Week 2 will populate these)
            'suggested_price':    float(self.suggested_price) if self.suggested_price else None,
            'price_confidence':   self.price_confidence,
            'market_average':     float(self.market_average) if self.market_average else None,
            'last_market_check':  self.last_market_check.isoformat() if self.last_market_check else None,
        }

    

    def __repr__(self):
        return (
            f"<Product(id={self.product_id}, "
            f"name='{self.name}', "
            f"condition='{self.condition}', "
            f"price={self.price})>"
        )