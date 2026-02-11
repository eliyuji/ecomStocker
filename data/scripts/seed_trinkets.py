"""
TrinketHub - Seed Data Script
Populates the database with realistic trinket listings for testing.
Run with: python data/scripts/seed_trinkets.py
"""
from config.database import SessionLocal, init_db
from modules.products.models import Product
from modules.auth.models import User
import random


# ============================================================
# SAMPLE TRINKET DATA
# Realistic items across all categories
# ============================================================
TRINKETS = [
    # --- Trading Cards ---
    {
        'name':                  'First Edition Charizard Pokemon Card',
        'category':              'Trading Cards',
        'subcategory':           'Pokemon Cards',
        'price':                 450.00,
        'brand':                 'Wizards of the Coast',
        'condition':             'near_mint',
        'year_manufactured':     1999,
        'rarity':                'ultra_rare',
        'material':              'cardboard',
        'dimensions':            '3.5x2.5 inches',
        'description':           'First edition base set Charizard. PSA-worthy condition.',
        'authenticity_verified': True,
    },
    {
        'name':                  'Holographic Blastoise Base Set',
        'category':              'Trading Cards',
        'subcategory':           'Pokemon Cards',
        'price':                 120.00,
        'brand':                 'Wizards of the Coast',
        'condition':             'excellent',
        'year_manufactured':     1999,
        'rarity':                'rare',
        'material':              'cardboard',
        'dimensions':            '3.5x2.5 inches',
        'description':           'Unlimited holographic Blastoise. Minor edgewear.',
        'authenticity_verified': False,
    },
    {
        'name':                  'Black Lotus Magic: The Gathering',
        'category':              'Trading Cards',
        'subcategory':           'Magic Cards',
        'price':                 3500.00,
        'brand':                 'Wizards of the Coast',
        'condition':             'good',
        'year_manufactured':     1993,
        'rarity':                'ultra_rare',
        'material':              'cardboard',
        'dimensions':            '3.5x2.5 inches',
        'description':           'Alpha Black Lotus. Play condition.',
        'authenticity_verified': True,
    },
    {
        'name':                  '1952 Mickey Mantle Topps Baseball Card',
        'category':              'Trading Cards',
        'subcategory':           'Sports Cards',
        'price':                 8500.00,
        'brand':                 'Topps',
        'condition':             'fair',
        'year_manufactured':     1952,
        'rarity':                'ultra_rare',
        'material':              'cardboard',
        'dimensions':            '2.625x3.75 inches',
        'description':           'Iconic rookie-era Mantle card. Shows age but intact.',
        'authenticity_verified': True,
    },

    # --- Vintage Toys ---
    {
        'name':                  'Original He-Man Action Figure',
        'category':              'Vintage Toys',
        'subcategory':           'Action Figures',
        'price':                 85.00,
        'brand':                 'Mattel',
        'condition':             'good',
        'year_manufactured':     1983,
        'rarity':                'uncommon',
        'material':              'plastic',
        'dimensions':            '5.5 inches tall',
        'description':           'Masters of the Universe He-Man. Includes power sword.',
        'authenticity_verified': False,
    },
    {
        'name':                  'Vintage G.I. Joe Snake Eyes Figure',
        'category':              'Vintage Toys',
        'subcategory':           'Action Figures',
        'price':                 110.00,
        'brand':                 'Hasbro',
        'condition':             'excellent',
        'year_manufactured':     1985,
        'rarity':                'rare',
        'material':              'plastic',
        'dimensions':            '3.75 inches tall',
        'description':           'Original all-black Snake Eyes with accessories.',
        'authenticity_verified': False,
    },
    {
        'name':                  'Star Wars Millennium Falcon (Vintage)',
        'category':              'Vintage Toys',
        'subcategory':           'Action Figures',
        'price':                 320.00,
        'brand':                 'Kenner',
        'condition':             'good',
        'year_manufactured':     1979,
        'rarity':                'rare',
        'material':              'plastic',
        'dimensions':            '22x19 inches',
        'description':           'Original Kenner Millennium Falcon. Working light and sound.',
        'authenticity_verified': False,
    },
    {
        'name':                  'LEGO Space Classic Set 928',
        'category':              'Vintage Toys',
        'subcategory':           'LEGO Sets',
        'price':                 380.00,
        'brand':                 'LEGO',
        'condition':             'excellent',
        'year_manufactured':     1979,
        'rarity':                'rare',
        'material':              'plastic',
        'dimensions':            'Box: 18x12 inches',
        'description':           'Galaxy Explorer set, 90% complete with original instructions.',
        'authenticity_verified': False,
    },

    # --- Jewelry ---
    {
        'name':                  'Art Deco Brooch - Gold Filigree',
        'category':              'Jewelry',
        'price':                 145.00,
        'brand':                 None,
        'condition':             'excellent',
        'year_manufactured':     1930,
        'rarity':                'uncommon',
        'material':              'gold',
        'dimensions':            '2x1.5 inches',
        'description':           '1930s Art Deco brooch with floral filigree. 10k gold.',
        'authenticity_verified': True,
    },
    {
        'name':                  'Victorian Cameo Pendant Necklace',
        'category':              'Jewelry',
        'price':                 210.00,
        'brand':                 None,
        'condition':             'good',
        'year_manufactured':     1890,
        'rarity':                'rare',
        'material':              'shell, gold',
        'dimensions':            'Pendant: 1.5x1 inches',
        'description':           'Shell cameo in gold-filled frame. Original chain included.',
        'authenticity_verified': True,
    },

    # --- Coins & Stamps ---
    {
        'name':                  '1909-S VDB Lincoln Cent',
        'category':              'Coins & Stamps',
        'price':                 750.00,
        'brand':                 'US Mint',
        'condition':             'good',
        'year_manufactured':     1909,
        'rarity':                'ultra_rare',
        'material':              'copper',
        'dimensions':            '19mm diameter',
        'description':           'Key date Lincoln cent. Low mintage, clear VDB initials.',
        'authenticity_verified': True,
    },
    {
        'name':                  'Inverted Jenny Stamp Replica',
        'category':              'Coins & Stamps',
        'price':                 45.00,
        'brand':                 'USPS',
        'condition':             'mint',
        'year_manufactured':     1918,
        'rarity':                'common',
        'material':              'paper',
        'dimensions':            '1.5x1 inches',
        'description':           'High-quality reproduction of famous inverted Jenny stamp.',
        'authenticity_verified': False,
    },

    # --- Figurines ---
    {
        'name':                  'Hummel Figurine - Apple Tree Boy',
        'category':              'Figurines',
        'price':                 95.00,
        'brand':                 'Goebel',
        'condition':             'excellent',
        'year_manufactured':     1965,
        'rarity':                'uncommon',
        'material':              'porcelain',
        'dimensions':            '6 inches tall',
        'description':           'Goebel Hummel Apple Tree Boy. No chips or cracks.',
        'authenticity_verified': True,
    },
    {
        'name':                  'Royal Doulton Character Jug - Falstaff',
        'category':              'Figurines',
        'price':                 65.00,
        'brand':                 'Royal Doulton',
        'condition':             'mint',
        'year_manufactured':     1950,
        'rarity':                'common',
        'material':              'ceramic',
        'dimensions':            '5.5 inches tall',
        'description':           'Large Falstaff character jug in original condition.',
        'authenticity_verified': False,
    },

    # --- Art & Prints ---
    {
        'name':                  'Original Watercolor - Mountain Lake Scene',
        'category':              'Art & Prints',
        'price':                 280.00,
        'brand':                 None,
        'condition':             'excellent',
        'year_manufactured':     1940,
        'rarity':                'rare',
        'material':              'paper, watercolor',
        'dimensions':            '12x9 inches',
        'description':           'Signed 1940s watercolor landscape. Slight foxing on edges.',
        'authenticity_verified': False,
    },

    # --- Memorabilia ---
    {
        'name':                  'Signed Babe Ruth Baseball (Replica)',
        'category':              'Memorabilia',
        'price':                 55.00,
        'brand':                 'Rawlings',
        'condition':             'mint',
        'year_manufactured':     2020,
        'rarity':                'common',
        'material':              'leather',
        'dimensions':            'Standard baseball',
        'description':           'Commemorative replica baseball with facsimile signature.',
        'authenticity_verified': False,
    },

    # --- Books & Comics ---
    {
        'name':                  'Amazing Fantasy #15 (Reprint)',
        'category':              'Books & Comics',
        'price':                 35.00,
        'brand':                 'Marvel',
        'condition':             'good',
        'year_manufactured':     1992,
        'rarity':                'common',
        'material':              'paper',
        'dimensions':            'Standard comic',
        'description':           '1992 reprint of Spider-Man\'s first appearance.',
        'authenticity_verified': False,
    },
    {
        'name':                  'First Edition The Hobbit Hardcover',
        'category':              'Books & Comics',
        'price':                 2800.00,
        'brand':                 'Allen & Unwin',
        'condition':             'fair',
        'year_manufactured':     1937,
        'rarity':                'ultra_rare',
        'material':              'paper, cloth binding',
        'dimensions':            '8.5x5.5 inches',
        'description':           'True 1st edition, 3rd impression. Jacket worn but present.',
        'authenticity_verified': True,
    },

    # --- Ceramics & Glassware ---
    {
        'name':                  'Vintage Fiesta Ware Pitcher - Cobalt Blue',
        'category':              'Ceramics & Glassware',
        'price':                 85.00,
        'brand':                 'Homer Laughlin',
        'condition':             'excellent',
        'year_manufactured':     1940,
        'rarity':                'uncommon',
        'material':              'ceramic',
        'dimensions':            '9 inches tall',
        'description':           'Original Fiesta ware in cobalt blue. No chips or crazing.',
        'authenticity_verified': False,
    },
    {
        'name':                  'Depression Glass Pink Cake Stand',
        'category':              'Ceramics & Glassware',
        'price':                 60.00,
        'brand':                 None,
        'condition':             'good',
        'year_manufactured':     1935,
        'rarity':                'common',
        'material':              'glass',
        'dimensions':            '11 inches diameter',
        'description':           'Pink depression glass cake stand. One tiny chip on base rim.',
        'authenticity_verified': False,
    },
]


def seed_users(db, count=20):
    """Create sample seller/buyer accounts"""
    print(f"  Creating {count} users...")
    for i in range(count):
        user = User(
            username   = f"collector{i+1}",
            email      = f"collector{i+1}@trinkethub.com",
            first_name = f"Collector",
            last_name  = f"#{i+1}",
        )
        user.set_password("password123")
        db.add(user)
    db.commit()
    print(f"  ✓ {count} users created")


def seed_trinkets(db):
    """Insert all trinket listings into the database"""
    print(f"  Creating {len(TRINKETS)} trinket listings...")

    for trinket_data in TRINKETS:
        product = Product(
            name                  = trinket_data['name'],
            category              = trinket_data.get('category'),
            subcategory           = trinket_data.get('subcategory'),
            price                 = trinket_data['price'],
            brand                 = trinket_data.get('brand'),
            description           = trinket_data.get('description', ''),
            stock_quantity        = 1,

            # Trinket-specific
            condition             = trinket_data.get('condition'),
            year_manufactured     = trinket_data.get('year_manufactured'),
            rarity                = trinket_data.get('rarity'),
            material              = trinket_data.get('material'),
            dimensions            = trinket_data.get('dimensions'),
            authenticity_verified = trinket_data.get('authenticity_verified', False),
        )
        db.add(product)

    db.commit()
    print(f"  ✓ {len(TRINKETS)} trinkets created")


def main():
    print("=" * 50)
    print("TrinketHub - Seed Data Script")
    print("=" * 50)

    init_db()
    db = SessionLocal()

    try:
        print("\nSeeding users...")
        seed_users(db, count=20)

        print("\nSeeding trinkets...")
        seed_trinkets(db)

        # Summary
        user_count    = db.query(User).count()
        product_count = db.query(Product).count()

        print(f"\n{'=' * 50}")
        print("Seed complete!")
        print(f"  Users:    {user_count}")
        print(f"  Trinkets: {product_count}")
        print(f"{'=' * 50}")
        print("\nStart the server: python app.py")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Error: {e}")
        raise

    finally:
        db.close()


if __name__ == '__main__':
    main()