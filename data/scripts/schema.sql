-- ============================================================
-- TrinketHub - Week 1 Database Schema
-- Run this file to set up all tables from scratch
-- Command: psql trinket_db < data/scripts/schema.sql
-- ============================================================

-- Drop tables if they exist (clean slate)
DROP TABLE IF EXISTS user_product_interactions CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS trinket_categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;


-- ============================================================
-- USERS TABLE
-- Stores buyer and seller accounts
-- ============================================================
CREATE TABLE users (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active     BOOLEAN DEFAULT TRUE
);


-- ============================================================
-- TRINKET CATEGORIES TABLE (NEW)
-- Predefined categories for trinkets/collectibles
-- Using a self-referencing table to allow parent/child categories
-- Example: parent = "Trading Cards", child = "Pokemon"
-- ============================================================
CREATE TABLE trinket_categories (
    category_id        SERIAL PRIMARY KEY,
    name               VARCHAR(100) UNIQUE NOT NULL,
    parent_category_id INT REFERENCES trinket_categories(category_id),  -- NULL = top-level
    description        TEXT,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed top-level categories
INSERT INTO trinket_categories (name, description) VALUES
    ('Trading Cards',        'Pokemon, Magic: The Gathering, sports cards'),
    ('Vintage Toys',         'Action figures, dolls, tin toys, board games'),
    ('Jewelry',              'Vintage and costume jewelry'),
    ('Coins & Stamps',       'Collectible coins, currency, postage stamps'),
    ('Figurines',            'Porcelain, resin, metal figurines and statues'),
    ('Vintage Electronics',  'Old gaming consoles, cameras, radios'),
    ('Art & Prints',         'Small paintings, prints, illustrations'),
    ('Memorabilia',          'Sports, movie, music memorabilia'),
    ('Books & Comics',       'Vintage books, comic books, magazines'),
    ('Ceramics & Glassware', 'Vintage pottery, vases, glassware');

-- Seed child categories (examples)
INSERT INTO trinket_categories (name, parent_category_id, description)
VALUES
    ('Pokemon Cards',   1, 'Pokemon trading cards, all sets'),
    ('Magic Cards',     1, 'Magic: The Gathering cards'),
    ('Sports Cards',    1, 'Baseball, basketball, football cards'),
    ('Action Figures',  2, 'G.I. Joe, He-Man, Star Wars figures'),
    ('LEGO Sets',       2, 'Vintage and retired LEGO sets');


-- ============================================================
-- PRODUCTS TABLE (MODIFIED FOR TRINKETS)
-- The core listing table - every trinket for sale lives here
-- ============================================================
CREATE TABLE products (
    product_id             SERIAL PRIMARY KEY,

    -- Basic info (existed before)
    name                   VARCHAR(255) NOT NULL,
    price                  DECIMAL(10,2) NOT NULL,
    description            TEXT,
    brand                  VARCHAR(100),
    stock_quantity         INT DEFAULT 1,           -- Usually 1 for unique trinkets
    image_url              VARCHAR(500),
    category_id INT REFERENCES trinket_categories(category_id),
    -- NEW: Trinket-specific fields
    condition              VARCHAR(50),             -- See VALID CONDITIONS below
    year_manufactured      INTEGER,                 -- e.g. 1985
    rarity                 VARCHAR(50),             -- See VALID RARITIES below
    material               VARCHAR(100),            -- e.g. 'ceramic', 'plastic', 'metal'
    dimensions             VARCHAR(100),            -- e.g. '5x3x2 inches'
    authenticity_verified  BOOLEAN DEFAULT FALSE,  -- Has item been verified authentic?

    -- NEW: Price intelligence fields (populated by Week 2 scraper)
    suggested_price        DECIMAL(10,2),           -- AI-suggested price
    price_confidence       VARCHAR(20),             -- 'high', 'medium', 'low'
    market_average         DECIMAL(10,2),           -- Average across eBay/Mercari/Etsy
    last_market_check      TIMESTAMP,               -- When was price last checked

    -- Timestamps
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active              BOOLEAN DEFAULT TRUE
);

-- VALID CONDITIONS (enforced in application layer, documented here):
-- 'mint'       - Perfect, unused, often still in packaging
-- 'near_mint'  - Barely used, minimal wear
-- 'excellent'  - Light use, no major defects
-- 'good'       - Normal wear, fully functional
-- 'fair'       - Heavy wear but intact
-- 'poor'       - Significant damage

-- VALID RARITIES:
-- 'common'      - Widely available
-- 'uncommon'    - Some scarcity
-- 'rare'        - Hard to find
-- 'ultra_rare'  - Very scarce, high demand


-- ============================================================
-- ORDERS TABLE
-- ============================================================
CREATE TABLE orders (
    order_id         SERIAL PRIMARY KEY,
    user_id          INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    total_amount     DECIMAL(10,2) NOT NULL,
    status           VARCHAR(50) DEFAULT 'pending',
    shipping_address TEXT,
    order_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_date     TIMESTAMP,
    delivered_date   TIMESTAMP
);


-- ============================================================
-- ORDER ITEMS TABLE
-- Links orders to products
-- ============================================================
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id      INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id    INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity      INT NOT NULL CHECK (quantity > 0),
    price         DECIMAL(10,2) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- REVIEWS TABLE
-- ============================================================
CREATE TABLE reviews (
    review_id         SERIAL PRIMARY KEY,
    user_id           INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    product_id        INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    rating            INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text       TEXT,
    review_title      VARCHAR(255),
    sentiment_score   DECIMAL(3,2),
    helpful_count     INT DEFAULT 0,
    verified_purchase BOOLEAN DEFAULT FALSE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)             -- One review per user per product
);


-- ============================================================
-- USER PRODUCT INTERACTIONS TABLE
-- Tracks views, saves, clicks (used for recommendations in Week 5)
-- ============================================================
CREATE TABLE user_product_interactions (
    interaction_id        SERIAL PRIMARY KEY,
    user_id               INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    product_id            INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    interaction_type      VARCHAR(50) NOT NULL,   -- 'view', 'save', 'click', 'purchase'
    interaction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- INDEXES
-- Speed up common queries
-- ============================================================
CREATE INDEX idx_users_email              ON users(email);
CREATE INDEX idx_products_category_id        ON products(category_id);
CREATE INDEX idx_products_condition       ON products(condition);
CREATE INDEX idx_products_rarity          ON products(rarity);
CREATE INDEX idx_products_price           ON products(price);
CREATE INDEX idx_products_year            ON products(year_manufactured);
CREATE INDEX idx_orders_user_id           ON orders(user_id);
CREATE INDEX idx_order_items_order_id     ON order_items(order_id);
CREATE INDEX idx_order_items_product_id   ON order_items(product_id);
CREATE INDEX idx_reviews_product_id       ON reviews(product_id);
CREATE INDEX idx_interactions_user_id     ON user_product_interactions(user_id);


-- ============================================================
-- AUTO-UPDATE TRIGGER
-- Automatically sets updated_at when a row changes
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();