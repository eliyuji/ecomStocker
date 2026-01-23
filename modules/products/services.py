"""
Product service - business logic for product operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from modules.products.models import Product
from typing import Optional, List

class ProductService:
    
    @staticmethod
    def create_product(db: Session, name: str, price: float, category: str = None,
                      subcategory: str = None, description: str = None, 
                      brand: str = None, stock_quantity: int = 0,
                      image_url: str = None) -> Product:
        """Create a new product"""
        product = Product(
            name=name,
            price=price,
            category=category,
            subcategory=subcategory,
            description=description,
            brand=brand,
            stock_quantity=stock_quantity,
            image_url=image_url
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return db.query(Product).filter(Product.product_id == product_id).first()
    
    @staticmethod
    def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_products_by_category(db: Session, category: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get products by category"""
        return db.query(Product).filter(
            Product.category == category,
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def search_products(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name, description, or brand"""
        search = f"%{query}%"
        return db.query(Product).filter(
            or_(
                Product.name.ilike(search),
                Product.description.ilike(search),
                Product.brand.ilike(search)
            ),
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_product(db: Session, product_id: int, **kwargs) -> Optional[Product]:
        """Update product information"""
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return None
        
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Soft delete a product (set is_active to False)"""
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return False
        
        product.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def update_stock(db: Session, product_id: int, quantity_change: int) -> Optional[Product]:
        """Update product stock quantity"""
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            return None
        
        product.stock_quantity += quantity_change
        db.commit()
        db.refresh(product)
        return product