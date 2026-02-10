# data/scripts/seed_trinkets.py

def seed_trinket_data(db):
    """Seed database with realistic trinket data"""
    
    trinkets = [
        {
            'name': 'First Edition Charizard Pokemon Card',
            'category': 'Trading Cards',
            'price': 450.00,
            'condition': 'near_mint',
            'year_manufactured': 1999,
            'rarity': 'ultra_rare',
            'material': 'cardboard',
            'dimensions': '3.5x2.5 inches',
            'description': 'First edition Charizard from Base Set...',
            'authenticity_verified': True
        },
        {
            'name': 'Vintage He-Man Action Figure',
            'category': 'Vintage Toys',
            'price': 85.00,
            'condition': 'good',
            'year_manufactured': 1983,
            'rarity': 'uncommon',
            'material': 'plastic',
            'dimensions': '5.5 inches tall',
            'description': 'Original Masters of the Universe...',
            'authenticity_verified': False
        },
        # ... more sample trinkets
    ]