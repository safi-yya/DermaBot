-- DermaBot Database Schema - Workshop MVP (Simplified)
DROP DATABASE IF EXISTS dermaBotDB;
CREATE DATABASE dermaBotDB;
\c dermaBotDB

-- USERS
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    birth_date DATE NOT NULL
);

-- AGE CATEGORY TABLE
CREATE TABLE age_category (
    age_category_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    age_category_label VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- SKIN TYPES TABLE
CREATE TABLE skin_types (
    skin_type_id SERIAL PRIMARY KEY,
    skin_type VARCHAR(100) NOT NULL UNIQUE
);

-- SKIN CONCERNS TABLE
CREATE TABLE skin_concerns (
    skin_concern_id SERIAL PRIMARY KEY,
    skin_concern VARCHAR(100) UNIQUE NOT NULL
);

-- USERS PROFILE TABLE
CREATE TABLE user_profile(
    profile_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    skin_type_id INT NOT NULL,
    skin_concern_id INT,
    age_category_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (skin_type_id) REFERENCES skin_types(skin_type_id),
    FOREIGN KEY (skin_concern_id) REFERENCES skin_concerns(skin_concern_id),
    FOREIGN KEY (age_category_id) REFERENCES age_category(age_category_id)
);

-- PRODUCTS
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    product_image TEXT, --*
    product_type VARCHAR(100) NOT NULL, -- face cream, tonic, serum, etc.
    product_category VARCHAR(100) NOT NULL, -- moisturizing, cleansing, etc.
    anti_aging_subcategory VARCHAR(100), -- can be null as not time not matter
    product_ingredients TEXT, --*
    frequency VARCHAR(20) NOT NULL, -- 'daily', 'weekly', or number
    timeOfDay VARCHAR(20) NOT NULL, -- 'morning', 'evening', 'both'
    stepOrder INT NOT NULL,
    totalVolumeMl DECIMAL(10,2),
    usagePerUseMl DECIMAL(10,2)
);

-- PRODUCT PROFILE TABLE
CREATE TABLE product_profile(
    product_profile_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    age_category_id INT,
    skin_type_id INT,
    skin_concern_id INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (age_category_id) REFERENCES age_category(age_category_id),
    FOREIGN KEY (skin_type_id) REFERENCES skin_types(skin_type_id),
    FOREIGN KEY (skin_concern_id) REFERENCES skin_concerns(skin_concern_id)
);

-- USER PRODUCT USAGE (routine + usage logs combined)
CREATE TABLE user_product_usage (
    log_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_in_routine BOOLEAN DEFAULT TRUE, -- whether this product is in user's active routine
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- REMINDERS TABLE
CREATE TABLE reminders (
    reminder_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    derma_activity VARCHAR(100) DEFAULT 'daily', --> pl face hidration mask or relaxation which takes time and you just do in certain time
    reminder_at TIMESTAMP NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =============================================
--  INSERT INTO Auto Generated
-- =============================================

-- Insert Skin Types
INSERT INTO skin_types (skin_type) VALUES
    ('Normal'),
    ('Dry'),
    ('Oily'),
    ('Combination'),
    ('Sensitive');

-- Insert Skin Concerns
INSERT INTO skin_concerns (skin_concern) VALUES
    ('Acne'),
    ('Redness'),
    ('Hyperpigmentation'),
    ('Fine Lines'),
    ('Wrinkles'),
    ('Dehydration'),
    ('Sun Damage'),
    ('Dark Spots'),
    ('Enlarged Pores'),
    ('Dullness');


-----------------------------------------
------- DermaBot Sample Data ------------
-----------------------------------------
-- 3 dummy data users with different skincare scenarios + 3 dummy products

INSERT INTO users (name, email, password, birth_date) VALUES 
    ('Emma Wilson', 'emma.wilson@email.com', 'hashed_password_123', '1999-06-12'),  -- 24 years old
    ('Sarah Chen', 'sarah.chen@email.com', 'hashed_password_456', '1989-03-15'),    -- 34 years old
    ('Lisa Rodriguez', 'lisa.rodriguez@email.com', 'hashed_password_789', '1981-09-22'); -- 42 years old


-- Insert Age Categories
INSERT INTO age_category (user_id, age_category_label)
SELECT 
    user_id,
    CASE
        WHEN age_years >= 2 AND age_years < 13 THEN '2-13'
        WHEN age_years >= 13 AND age_years < 20 THEN '13-20'
        WHEN age_years >= 20 AND age_years < 30 THEN '20-30'
        WHEN age_years >= 30 AND age_years < 35 THEN '30-35'
        WHEN age_years >= 35 AND age_years < 40 THEN '35-40'
        WHEN age_years >= 40 AND age_years < 45 THEN '40-45'
        WHEN age_years >= 45 AND age_years < 50 THEN '45-50'
        WHEN age_years >= 50 AND age_years < 55 THEN '50-55'
        WHEN age_years >= 55 AND age_years < 60 THEN '55-60'
        WHEN age_years >= 60 THEN '60+'
        ELSE 'N/A'
    END AS age_category_label
FROM (
    SELECT user_id, DATE_PART('year', AGE(CURRENT_DATE, birth_date)) AS age_years
    FROM users
) AS sub;


INSERT INTO products (name, frequency, timeOfDay, stepOrder, totalVolumeMl, usagePerUseMl, product_type, product_category, anti_aging_subcategory) VALUES 
    -- Basic cleanser for everyone
    ('Gentle Daily Cleanser', 'daily', 'both', 1, 200.0, 2.5, 'Cleanser', 'Cleansing', NULL),
    -- Preventive serum for young adults
    ('Vitamin C Brightening Serum', 'daily', 'morning', 2, 30.0, 0.5, 'Serum', 'Brightening', 'Prevention'),
    -- Anti-aging night treatment for mature skin
    ('Retinol Night Treatment', '3', 'evening', 3, 25.0, 0.3, 'Treatment', 'Anti-Aging', 'Wrinkle Reduction');


-- skin profiles
INSERT INTO user_profile (user_id, skin_type_id, skin_concern_id) VALUES
    (1, 1, 10),  -- Emma: Normal skin, concerned about dullness (prevention)
    (2, 4, 4),   -- Sarah: Combination skin, concerned about fine lines
    (3, 2, 5);   -- Lisa: Dry skin, concerned about wrinkles

-- product_profiles
INSERT INTO product_profile (product_id, age_category_id, skin_type_id, skin_concern_id) VALUES
    -- Cleanser: suitable for everyone
    (1, 1, 1, NULL), (1, 1, 4, NULL), (1, 1, 2, NULL),  -- 20-30 age group, all skin types
    (1, 2, 1, NULL), (1, 2, 4, NULL), (1, 2, 2, NULL),  -- 30-40 age group, all skin types
    (1, 3, 1, NULL), (1, 3, 4, NULL), (1, 3, 2, NULL),  -- 40-50 age group, all skin types
    
    -- Vitamin C Serum: great for prevention and brightening
    (2, 1, 1, 10),  -- 20-30, normal skin, dullness
    (2, 2, 4, 4),   -- 30-40, combination skin, fine lines
    (2, 3, 2, 10),  -- 40-50, dry skin, dullness
    
    -- Retinol: best for 30+ with aging concerns
    (3, 2, 4, 4),   -- 30-40, combination skin, fine lines
    (3, 3, 2, 5);   -- 40-50, dry skin, wrinkles

-- =============================================
-- USER SCENARIOS & ROUTINES
-- =============================================

-- Scenario 1: Emma (24) - Simple prevention routin -- Cleanser daily + Vitamin C serum for prevention
INSERT INTO user_product_usage (user_id, product_id, used_at, is_in_routine) VALUES
    -- Emma: cleanser morning & evening
    (1, 1, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),        -- Used cleanser yesterday evening
    (1, 1, CURRENT_TIMESTAMP - INTERVAL '12 hours', TRUE),     -- Used cleanser this morning
    (1, 1, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),       -- Used cleanser 2 days ago
    -- Emma: vitamin C serum every morning
    (1, 2, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),        -- Used serum yesterday morning
    (1, 2, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),       -- Used serum 2 days ago
    (1, 2, CURRENT_TIMESTAMP - INTERVAL '3 days', TRUE);       -- Used serum 3 days ago

-- Scenario 2: Sarah (34) - Moderate anti-aging routine -- Cleanser + Vitamin C serum + occasional retinol
INSERT INTO user_product_usage (user_id, product_id, used_at, is_in_routine) VALUES
    -- Sarah's routine: Cleanser daily
    (2, 1, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),        -- Used cleanser yesterday
    (2, 1, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),       -- Used cleanser 2 days ago
    -- Sarah's routine: Vitamin C serum daily
    (2, 2, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),        -- Used serum yesterday
    (2, 2, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),       -- Used serum 2 days ago
    -- Sarah's routine: Retinol every 3 days (started recently)
    (2, 3, CURRENT_TIMESTAMP - INTERVAL '3 days', TRUE),       -- Used retinol 3 days ago (should use today!)
    (2, 3, CURRENT_TIMESTAMP - INTERVAL '6 days', TRUE);       -- Used retinol 6 days ago

-- Scenario 3: Lisa (42) - Intensive anti-aging routine -- all products
INSERT INTO user_product_usage (user_id, product_id, used_at, is_in_routine) VALUES
    -- Lisa's routine: Cleanser twice daily (very consistent)
    (3, 1, CURRENT_TIMESTAMP - INTERVAL '12 hours', TRUE),     -- Used this morning
    (3, 1, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),        -- Used yesterday evening
    (3, 1, CURRENT_TIMESTAMP - INTERVAL '1 day 12 hours', TRUE), -- Used yesterday morning
    (3, 1, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),       -- Used 2 days ago
    
    -- Lisa's routine: Vitamin C serum daily (morning)
    (3, 2, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),        -- Used yesterday
    (3, 2, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),       -- Used 2 days ago
    (3, 2, CURRENT_TIMESTAMP - INTERVAL '3 days', TRUE),       -- Used 3 days ago
    
    -- Lisa's routine: Retinol very regularly (every 3 days)
    (3, 3, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),        -- Used yesterday (intensive routine)
    (3, 3, CURRENT_TIMESTAMP - INTERVAL '4 days', TRUE),       -- Used 4 days ago
    (3, 3, CURRENT_TIMESTAMP - INTERVAL '7 days', TRUE);       -- Used 1 week ago



--- Run basic queries to save into txt file
SELECT * FROM users;
SELECT * FROM age_category;
SELECT * FROM skin_types;
SELECT * FROM skin_concerns;
SELECT * FROM user_profile;
SELECT * FROM products;
SELECT * FROM product_profile;
SELECT * FROM user_product_usage;
SELECT * FROM reminders;