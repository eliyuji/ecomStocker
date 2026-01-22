"""
Review model
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class Review(Base):
    __tablename__ = 'reviews'
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='unique_user_product_review'),
    )
    
    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    review_title = Column(String(255))
    sentiment_score = Column(Numeric(3, 2))
    helpful_count = Column(Integer, default=0)
    verified_purchase = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'review_id': self.review_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_title': self.review_title,
            'sentiment_score': float(self.sentiment_score) if self.sentiment_score else None,
            'helpful_count': self.helpful_count,
            'verified_purchase': self.verified_purchase,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'username': self.user.username if self.user else None
        }
    
    def __repr__(self):
        return f"<Review(id={self.review_id}, product_id={self.product_id}, rating={self.rating})>"

class UserProductInteraction(Base):
    __tablename__ = 'user_product_interactions'
    
    interaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    interaction_type = Column(String(50), nullable=False)
    interaction_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'interaction_id': self.interaction_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'interaction_type': self.interaction_type,
            'interaction_timestamp': self.interaction_timestamp.isoformat() if self.interaction_timestamp else None
        }
    
    def __repr__(self):
        return f"<Interaction(id={self.interaction_id}, user={self.user_id}, product={self.product_id}, type={self.interaction_type})>"