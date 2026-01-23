"""
User service - business logic for user operations
"""
from sqlalchemy.orm import Session
from modules.auth.models import User
from typing import Optional, List

class UserService:
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, 
                   first_name: str = None, last_name: str = None) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and key != 'password_hash':
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = UserService.get_user_by_email(db, email)
        if not user or not user.check_password(password):
            return None
        return user