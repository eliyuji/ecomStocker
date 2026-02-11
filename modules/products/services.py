"""
Product service - business logic for product operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from modules.products.models import Product, VALID_CONDITIONS, VALID_RARITIES
from typing import Optional, List

class ProductService:
    """"year_manufactured": 1999
        "condition": "near-mint"
        "material": "plastic"
        "description": "A rare vintage item from 1999..."
        "authenticity_verified": true"""
    
    @staticmethod
    def create_product(db: Session, name: str, price: float, category: str = None,
                      subcategory: str = None, description: str = None, 
                      brand: str = None, stock_quantity: int = 0,
                      image_url: str = None, year_manufactured: int = None, condition: str = None, material: str = None,
                      authenticity_verified: bool = False ) -> Product:
        """Create a new product"""
        product = Product(
            name=name,
            price=price,
            category=category,
            subcategory=subcategory,
            description=description,
            brand=brand,
            stock_quantity=stock_quantity,
            image_url=image_url,
            year_manufactured=year_manufactured,
            condition=condition,
            material=material,
            authenticity_verified=authenticity_verified
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
    def get_products_by_category_id(db: Session, category_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get products by category"""
        return (
            db.query(Product)
            .filter(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
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

    @staticmethod
    def is_overpriced(product):
        """
        Returns True if listing price is more than 20% above market average.
        """
        if not product.market_average:
            return None
        return float(product.price) > float(product.market_average) * 1.2

    @staticmethod
    def is_underpriced(product):
        """
        Returns True if listing price is more than 20% below market average.
        """
        if not product.market_average:
            return None
        return float(product.price) < float(product.market_average) * 0.8
    
    @staticmethod
    def filter_products(db: Session, category:str = None, 
                        condition: str = None,
                        rarity: str = None,
                        year_min: int = None,
                        year_max: int = None,
                        price_min: float = None,
                        price_max: float = None,
                        skip: int = 0,
                        limit: int = 100) -> List[Product]:
        """Filter products based on multiple criteria"""
        if category:
            query = db.query.filter(Product.category_id == category)
        if condition:
            query = query.filter(Product.condition == condition)
        if rarity:
            query = query.filter(Product.rarity == rarity)
        if year_min:
            query = query.filter(Product.year_manufactured >= year_min)
        if year_max:
            query = query.filter(Product.year_manufactured <= year_max)
        if price_min:
            query = query.filter(Product.price >= price_min)
        if price_max:
            query = query.filter(Product.price <= price_max)

        return query.filter(Product.is_active == True).offset(skip).limit(limit).all()
    @staticmethod
    def get_by_condition(db: Session, condition: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get products by condition (e.g. "mint", "near-mint", "used")
        Returns all products matching the specified condition
        """
        return db.query(Product).filter(Product.condition == condition, Product.is_active == True).offset(skip).limit(limit).all()
    @staticmethod
    def get_by_rarity(db: Session, rarity: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Get products by rarity (e.g. "common", "uncommon", "rare")
        Returns all products matching the specified rarity
        """
        return db.query(Product).filter(Product.rarity == rarity, Product.is_active == True).offset(skip).limit(limit).all()
    @staticmethod
    def validate_trinket_fields(condition: str = None, rarity: str = None) -> List[str]:
        """
        Validate trinket-specific fields
        """
        errors = []
        if condition and condition not in VALID_CONDITIONS:
            errors.append(f"Invalid condition: {condition}. Must be one of {', '.join(VALID_CONDITIONS)}")
        if rarity and rarity not in VALID_RARITIES:
            errors.append(f"Invalid rarity: {rarity}. Must be one of {', '.join(VALID_RARITIES)}")
        return errors