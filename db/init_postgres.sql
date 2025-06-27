-- PostgreSQL Database Schema for E-commerce Customer Analytics

-- Create database if not exists
-- CREATE DATABASE customer_events;

-- Connect to the database
-- \c customer_events;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Create customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 0 AND age <= 120),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create events table
CREATE TABLE events (
    event_id VARCHAR(255) PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER REFERENCES products(product_id),
    product_title VARCHAR(255),
    product_price DECIMAL(10,2),
    product_image VARCHAR(500),
    action VARCHAR(50) NOT NULL CHECK (action IN ('add_to_cart', 'remove_from_cart', 'purchase_cart')),
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255),
    user_agent TEXT,
    ip_address INET
);

-- Insert more sample products to replace unknown products
INSERT INTO products (title, price, description, image_url, category) VALUES
('Wireless Bluetooth Headphones', 89.99, 'High-quality wireless headphones with noise cancellation', 'https://example.com/headphones.jpg', 'Electronics'),
('Smart Fitness Watch', 199.99, 'Track your fitness goals with this advanced smartwatch', 'https://example.com/watch.jpg', 'Electronics'),
('Organic Cotton T-Shirt', 29.99, 'Comfortable and eco-friendly cotton t-shirt', 'https://example.com/tshirt.jpg', 'Clothing'),
('Stainless Steel Water Bottle', 24.99, 'Keep your drinks cold for hours with this insulated bottle', 'https://example.com/bottle.jpg', 'Home'),
('Wireless Phone Charger', 49.99, 'Fast wireless charging pad for your smartphone', 'https://example.com/charger.jpg', 'Electronics'),
('Yoga Mat', 39.99, 'Non-slip yoga mat perfect for home workouts', 'https://example.com/yoga.jpg', 'Sports'),
('Coffee Maker', 79.99, 'Programmable coffee maker with thermal carafe', 'https://example.com/coffee.jpg', 'Home'),
('Running Shoes', 129.99, 'Lightweight running shoes with excellent cushioning', 'https://example.com/shoes.jpg', 'Sports'),
('Laptop Stand', 34.99, 'Adjustable laptop stand for better ergonomics', 'https://example.com/stand.jpg', 'Electronics'),
('Plant Pot Set', 19.99, 'Beautiful ceramic plant pots for your indoor garden', 'https://example.com/pots.jpg', 'Home'),
('Gaming Mouse', 59.99, 'High-precision gaming mouse with RGB lighting', 'https://example.com/mouse.jpg', 'Electronics'),
('Backpack', 45.99, 'Durable backpack with laptop compartment', 'https://example.com/backpack.jpg', 'Clothing'),
('Desk Lamp', 29.99, 'Adjustable LED desk lamp with USB port', 'https://example.com/lamp.jpg', 'Home'),
('Bluetooth Speaker', 79.99, 'Portable waterproof bluetooth speaker', 'https://example.com/speaker.jpg', 'Electronics'),
('Sunglasses', 89.99, 'Polarized sunglasses with UV protection', 'https://example.com/sunglasses.jpg', 'Clothing'),
('Kitchen Knife Set', 149.99, 'Professional kitchen knife set with block', 'https://example.com/knives.jpg', 'Home'),
('Resistance Bands', 24.99, 'Set of 5 resistance bands for home workouts', 'https://example.com/bands.jpg', 'Sports'),
('Phone Case', 19.99, 'Protective phone case with kickstand', 'https://example.com/case.jpg', 'Electronics'),
('Throw Pillow', 15.99, 'Soft decorative throw pillow for home', 'https://example.com/pillow.jpg', 'Home'),
('Hair Dryer', 69.99, 'Professional hair dryer with multiple settings', 'https://example.com/hairdryer.jpg', 'Beauty');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_customer_id ON events(customer_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_action ON events(action);
CREATE INDEX IF NOT EXISTS idx_events_product_id ON events(product_id);

-- Create a view for abandoned carts analysis (customers with cart activity but no purchases)
CREATE OR REPLACE VIEW abandoned_carts AS
SELECT 
    customer_id,
    COUNT(*) as cart_events,
    MAX(timestamp) as last_activity,
    STRING_AGG(DISTINCT product_title, ', ') as abandoned_products,
    SUM(product_price) as total_abandoned_value
FROM events 
WHERE action IN ('add_to_cart', 'remove_from_cart')
AND customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM events 
    WHERE action = 'purchase_cart'
)
GROUP BY customer_id;

-- Create a view for conversion funnel
CREATE OR REPLACE VIEW conversion_funnel AS
SELECT 
    action,
    COUNT(*) as event_count,
    COUNT(DISTINCT customer_id) as unique_customers
FROM events 
GROUP BY action
ORDER BY 
    CASE action 
        WHEN 'add_to_cart' THEN 1
        WHEN 'purchase_cart' THEN 2
        ELSE 3
    END;

-- Create a view for seasonal trends
CREATE OR REPLACE VIEW seasonal_trends AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour_bucket,
    DATE_TRUNC('day', timestamp) as day_bucket,
    DATE_TRUNC('week', timestamp) as week_bucket,
    DATE_TRUNC('month', timestamp) as month_bucket,
    action,
    COUNT(*) as event_count,
    COUNT(DISTINCT customer_id) as unique_customers
FROM events 
GROUP BY 
    DATE_TRUNC('hour', timestamp),
    DATE_TRUNC('day', timestamp),
    DATE_TRUNC('week', timestamp),
    DATE_TRUNC('month', timestamp),
    action;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
