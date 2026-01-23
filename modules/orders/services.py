"""
Order service - business logic for order operations
"""
from sqlalchemy.orm import Session
from modules.orders.models import Order, OrderItem
from modules.products.services import ProductService
from typing import Optional, List, Dict

class OrderService:
    
    @staticmethod
    def create_order(db: Session, user_id: int, items: List[Dict], 
                    shipping_address: str = None) -> Optional[Order]:
        """
        Create a new order with items
        items format: [{'product_id': 1, 'quantity': 2}, ...]
        """
        total_amount = 0
        order_items = []
        
        # Validate and calculate total
        for item in items:
            product = ProductService.get_product_by_id(db, item['product_id'])
            if not product:
                return None
            
            if product.stock_quantity < item['quantity']:
                raise ValueError(f"Insufficient stock for product {product.name}")
            
            item_price = product.price * item['quantity']
            total_amount += item_price
            
            order_items.append({
                'product_id': product.product_id,
                'quantity': item['quantity'],
                'price': product.price
            })
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            status='pending'
        )
        
        db.add(order)
        db.flush()  # Get order_id without committing
        
        # Create order items and update stock
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.add(order_item)
            
            # Update product stock
            ProductService.update_stock(db, item_data['product_id'], -item_data['quantity'])
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return db.query(Order).filter(Order.order_id == order_id).first()
    
    @staticmethod
    def get_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders for a user"""
        return db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders with pagination"""
        return db.query(Order).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_order_status(db: Session, order_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return None
        
        order.status = status
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def cancel_order(db: Session, order_id: int) -> bool:
        """Cancel an order and restore stock"""
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order or order.status not in ['pending', 'processing']:
            return False
        
        # Restore stock
        for item in order.order_items:
            ProductService.update_stock(db, item.product_id, item.quantity)
        
        order.status = 'cancelled'
        db.commit()
        return True