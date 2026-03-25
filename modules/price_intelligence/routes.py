  # API endpoints
"""
Price Intelligence Routes
HTTP endpoints for all price intelligence features.

All routes prefixed with /api/price/

ENDPOINTS SUMMARY:
    POST /api/price/check                    One-off price check (no product_id needed)
    GET  /api/price/product/<product_id>     Full intelligence for a saved product
    POST /api/price/product/<product_id>/refresh   Force re-scrape for a product
    GET  /api/price/history/<product_id>     Historical price checks for a product
    POST /api/price/alerts/                  Create a price alert
    GET  /api/price/alerts/<user_id>         Get all alerts for a user
    DELETE /api/price/alerts/<alert_id>      Delete an alert
"""
from flask import Blueprint, request, jsonify
from config.database import SessionLocal
from modules.price_intelligence.services import PriceIntelligenceService
from modules.price_intelligence.models import PriceAlert

price_bp = Blueprint('price_intelligence', __name__, url_prefix='/api/price')

@price_bp.route('/check', methods= ['POST'])
def check__price():
  db = SessionLocal()
  try:
    data = request.get_json()
    if 'product_name' not in data:
      return jsonify({'product_name not found in database'}), 400
    result = PriceIntelligenceService.check_market_price(db, data.get('product_name'), data.get('category'), data.get('condition'))
    if 'error' in result:
      return 404
    else:
      return jsonify(result), 200
  except Exception as e:
    db.rollback()
    return jsonify({'error': str(e)}), 500
  finally:
    db.close()

@price_bp.route('/product/<int:product_id>', methods= ['GET'])
def get_product_intelligence(product_id):
  db= SessionLocal()
  try:
    result = PriceIntelligenceService.get_product_intelligence(db,product_id)
    if 'error' in result:
      return jsonify({'error'}), 404
    return jsonify(result), 200
  
  except Exception as e:
    db.rollback()
    return jsonify({'error': str(e)}), 500
  finally:
    db.close()

@price_bp.route('/product/<int:product_id>/refresh', methods=['POST'])
def refresh_product_price(product_id):
  db = SessionLocal()
  try:
    result = PriceIntelligenceService.check_and_save_product_price(db,product_id)
    if result is None:
      return jsonify({'error'}), 404
    else:
      return jsonify(result), 200
  except Exception as e:
    db.rollback()
    return jsonify({'error': str(e)}), 500
  finally:
    db.close()

@price_bp.route('/history/<int:product_id>', methods = ['GET'])
def get_price_history(product_id):
  db = SessionLocal()
  try:
    result = PriceIntelligenceService.get_price_history(db,product_id)
    return jsonify({result}), 200
  finally:
    db.close()
@price_bp.route('/alerts/', methods=['POST'])
def create_alert():
  """
    Create a price alert for a product.

    POST /api/price/alerts/

    REQUEST BODY:
    {
        "user_id":    1,
        "product_id": 5,
        "alert_type": "price_drop",       ('price_drop', 'price_increase', 'price_target')
        "target_price": 100.00            (optional - trigger when market hits this)
    }
  """
  db = SessionLocal()
  try:
    data = request.get_json()
    if not data:
      return jsonify({'error': 'Request body is required'}), 400
  
    required_fields = ['user_id', 'product_id', 'alert_type']
    if not all(field in data for field in required_fields):
      return jsonify({'error': 'Missing required fields'}), 400
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    alert_type = data.get('alert_type')
    target_price = data.get('target_price')

    alert_types = ['price_drop', 'price_increase', 'price_target']
    if target_price not in alert_types:
      return jsonify({'error': 'Not valid alert type'}), 400
    if target_price == 'price_target' and target_price is None:
      return jsonify({'error': 'target_price is required when alert_type is price_target'}), 400
    
    alert= PriceAlert(
      user_id=user_id,
      product_id=product_id,
      alert_type=alert_type,
      target_price=target_price)
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return jsonify(alert.to_dict()), 201

  except Exception as e:
    db.rollback()
    return jsonify({'error': str(e)}), 500
  finally:
    db.close()
@price_bp.route('/alerts/user/<int:user_id>', methods=['GET'])
def get_user_alerts(user_id):
    """
    Get all active price alerts for a user.

    GET /api/price/alerts/user/1

    WHAT TO DO:
        1. Query PriceAlert where user_id = user_id AND is_active = True
        2. Return [alert.to_dict() for alert in alerts], 200
    """
    db = SessionLocal()
    try:
        alerts = (db.query(PriceAlert)
                 .filter_by(user_id=user_id, is_active=True)
                 )
        return [alert.to_dict() for alert in alerts], 200
    except Exception as e:
      return jsonify({'error': str(e)})
    finally:
        db.close()


@price_bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """
    Deactivate a price alert (soft delete - sets is_active = False).

    DELETE /api/price/alerts/3

    WHAT TO DO:
        1. Query PriceAlert by alert_id
        2. If not found, return 404
        3. Set alert.is_active = False, db.commit()
        4. Return { 'message': 'Alert deleted' }, 200
    """
    db = SessionLocal()
    try:
        alert = db.query(PriceAlert).filter_by(alert_id=alert_id).first()
        if not alert:
          return jsonify({'error': f'{alert_id} not found'}) 
        alert.is_active = False
        db.commit()
        return jsonify({'message': 'Alert Deleted'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()