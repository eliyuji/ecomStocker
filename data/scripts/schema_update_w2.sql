-- ============================================================
-- TrinketHub - Week 2 Schema Updates
-- Adds tables needed for price intelligence
-- Run AFTER schema_week1.sql:
--   psql trinket_hub schema_update_w2.sql
-- ============================================================

-- ============================================================
--  Everytime we scrape the internet for a product's market price, we store a summary row 
-- Used to see how a products price changes over time
-- ============================================================
CREATE TABLE IF NOT EXISTS price_checks (
    check_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    source VARCHAR(500) NOT NULL, -- e.g. "Amazon", "eBay", "Newtype"
    average_price DECIMAL(10, 2), -- Average price found across all sources
    median_price DECIMAL(10, 2), -- Median price found across all sources
    min_price DECIMAL(10, 2),
    max_price DECIMAL(10, 2),
    sample_size INT, -- Number of sold listings found
    --confidence DECIMAL(5, 2), -- Optional: A confidence score for the price data (e.g. based on sample size or variance)
    raw_data JSONB, -- Store the raw price data from different sources for reference
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

CREATE INDEX idx_price_checks_product ON price_checks(product_id);
CREATE INDEX idx_price_checks_source ON price_checks(source);
-- Optional: If you want to query by date range
CREATE INDEX idx_price_checks_date ON price_checks(checked_at);

-- ============================================================
-- MARKET SALES TABLE
-- Individual sold listings scraped from external platforms.
-- Each row = one sold item from eBay, Mercari, or Etsy.
-- Used by the analyzer to calculate averages and trends.
-- ============================================================
CREATE TABLE IF NOT EXISTS market_sales (
    sale_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    condition VARCHAR(50),
    sold_price DECIMAL(10, 2) NOT NULL,
    sold_date DATE,
    source VARCHAR(50),
    source__url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
CREATE INDEX idx_market_sales_name ON market_sales(product_name);
CREATE INDEX idx_market_sales_category ON market_sales(category);
CREATE INDEX idx_market_sales_source ON market_sales(source);
CREATE INDEX idx_market_sales_date ON market_sales(sold_date)

-- ============================================================
-- PRICE ALERTS TABLE
-- Users can set up alerts to be notified when market price
-- hits a target (e.g. "tell me when Charizard drops below $100")
-- ============================================================
CREATE TABLE IF NOT EXISTS price_alerts (
    alert_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    product_id INT NOT NULL REFERENCES products(product_id)
    alert_type VARCHAR(50) NOT NULL, -- e.g. "below", "above", "percentage_drop"
    target_price DECIMAL(10,2)
    percentage_drop INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered_at TIMESTAMP
);

CREATE INDEX idx_price_alerts_user ON price_alerts(user_id);
CREATE INDEX idx_price_alerts_product ON price_alerts(product_id);
CREATE INDEX idx_price_alerts_active ON price_alerts(is_active);

CREATE TABLE IF NOT EXISTS alert_triggers (
    notification_id SERIAL PRIMARY KEY,
    alert_id INT NOT NULL REFERENCES price_alerts(alert_id),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    notification_sent BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    notification_method VARCHAR(50), -- e.g. "email", "sms", "in-app"
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);