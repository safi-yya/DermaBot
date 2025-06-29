"""
DermaBot Database Seeder
Creates database tables and inserts sample data
"""
from db.connection import create_conn, close_db

def seed():
    conn = create_conn()
    
    try:
        print("Creating DermaBot database...")
        
        # ----- Drop existing tables -----
        conn.run("DROP TABLE IF EXISTS reminders CASCADE;")
        conn.run("DROP TABLE IF EXISTS user_product_usage CASCADE;")
        conn.run("DROP TABLE IF EXISTS product_profile CASCADE;")
        conn.run("DROP TABLE IF EXISTS user_profile CASCADE;")
        conn.run("DROP TABLE IF EXISTS age_category CASCADE;")
        conn.run("DROP TABLE IF EXISTS products CASCADE;")
        conn.run("DROP TABLE IF EXISTS skin_concerns CASCADE;")
        conn.run("DROP TABLE IF EXISTS skin_types CASCADE;")
        conn.run("DROP TABLE IF EXISTS users CASCADE;")
        

        # ----- Create tables -----
        print("Creating tables...")
        
        # USERS table
        conn.run("""
            CREATE TABLE users (
                user_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                birth_date DATE NOT NULL
            );
        """)
        
        # SKIN TYPES table
        conn.run("""
            CREATE TABLE skin_types (
                skin_type_id SERIAL PRIMARY KEY,
                skin_type VARCHAR(100) NOT NULL UNIQUE
            );
        """)
        
        # SKIN CONCERNS table
        conn.run("""
            CREATE TABLE skin_concerns (
                skin_concern_id SERIAL PRIMARY KEY,
                skin_concern VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        
        # AGE CATEGORY table
        conn.run("""
            CREATE TABLE age_category (
                age_category_id SERIAL PRIMARY KEY,
                user_id INT UNIQUE NOT NULL,
                age_category_label VARCHAR(50) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)
        
        # USER PROFILE table
        conn.run("""
            CREATE TABLE user_profile(
                profile_id SERIAL PRIMARY KEY,
                user_id INT UNIQUE NOT NULL,
                skin_type_id INT NOT NULL,
                skin_concern_id INT,
                age_category_id INT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (skin_type_id) REFERENCES skin_types(skin_type_id),
                FOREIGN KEY (skin_concern_id) REFERENCES skin_concerns(skin_concern_id)
                FOREIGN KEY (age_category_id) REFERENCES age_category(age_category_id)
            );
        """)
        
        # PRODUCTS table
        conn.run("""
            CREATE TABLE products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                product_image TEXT,
                product_type VARCHAR(100) NOT NULL,
                product_category VARCHAR(100) NOT NULL,
                anti_aging_subcategory VARCHAR(100),
                product_ingredients TEXT,
                frequency VARCHAR(20) NOT NULL,
                timeOfDay VARCHAR(20) NOT NULL,
                stepOrder INT NOT NULL,
                totalVolumeMl DECIMAL(10,2),
                usagePerUseMl DECIMAL(10,2)
            );
        """)
        
        # PRODUCT PROFILE table
        conn.run("""
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
        """)
        
        # USER PRODUCT USAGE table
        conn.run("""
            CREATE TABLE user_product_usage (
                log_id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_in_routine BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """)
        
        # REMINDERS table
        conn.run("""
            CREATE TABLE reminders (
                reminder_id SERIAL PRIMARY KEY,
                product_id INT NOT NULL,
                user_id INT NOT NULL,
                derma_activity VARCHAR(100) DEFAULT 'daily',
                reminder_at TIMESTAMP NOT NULL,
                sent BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)
        
        print("All tables created successfully!")
        
        # ----- Insert reference data -----
        print("Inserting reference data...")
        
        # Insert skin types
        conn.run("""
            INSERT INTO skin_types (skin_type) VALUES
                ('Normal'),
                ('Dry'),
                ('Oily'),
                ('Combination'),
                ('Sensitive');
        """)
        
        # Insert skin concerns
        conn.run("""
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
        """)
        
        # ----- Insert sample dummy data users -----
        print("Creating sample users...")
        
        conn.run("""
            INSERT INTO users (name, email, password, birth_date) VALUES 
                ('Emma Wilson', 'emma.wilson@email.com', 'hashed_password_123', '1999-06-12'),
                ('Sarah Chen', 'sarah.chen@email.com', 'hashed_password_456', '1989-03-15'),
                ('Lisa Rodriguez', 'lisa.rodriguez@email.com', 'hashed_password_789', '1981-09-22');
        """)
        
        # Insert age categories for users
        conn.run("""
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
        """)
        
        # Insert user profiles
        conn.run("""
            INSERT INTO user_profile (user_id, skin_type_id, skin_concern_id) VALUES
                (1, 1, 10),  -- Emma: Normal skin, dullness
                (2, 4, 4),   -- Sarah: Combination skin, fine lines
                (3, 2, 5);   -- Lisa: Dry skin, wrinkles
        """)
        
        # ----- Insert sample products -----
        print("Creating sample products...")
        
        conn.run("""
            INSERT INTO products (name, frequency, timeOfDay, stepOrder, totalVolumeMl, usagePerUseMl, product_type, product_category, anti_aging_subcategory) VALUES 
                ('Gentle Daily Cleanser', 'daily', 'both', 1, 200.0, 2.5, 'Cleanser', 'Cleansing', NULL),
                ('Vitamin C Brightening Serum', 'daily', 'morning', 2, 30.0, 0.5, 'Serum', 'Brightening', 'Prevention'),
                ('Retinol Night Treatment', '3', 'evening', 3, 25.0, 0.3, 'Treatment', 'Anti-Aging', 'Wrinkle Reduction');
        """)
        
        # Insert product profiles
        conn.run("""
            INSERT INTO product_profile (product_id, age_category_id, skin_type_id, skin_concern_id) VALUES
                (1, 1, 1, NULL), (1, 2, 4, NULL), (1, 3, 2, NULL),
                (2, 1, 1, 10), (2, 2, 4, 4), (2, 3, 2, 10),
                (3, 2, 4, 4), (3, 3, 2, 5);
        """)
        
        # ----- Insert usage history -----
        print("Creating usage history...")
        
        # Emma's usage history
        conn.run("""
            INSERT INTO user_product_usage (user_id, product_id, used_at, is_in_routine) VALUES
                -- Emma: cleanser usage
                (1, 1, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),
                (1, 1, CURRENT_TIMESTAMP - INTERVAL '12 hours', TRUE),
                (1, 1, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),
                -- Emma: vitamin C serum usage
                (1, 2, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),
                (1, 2, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),
                (1, 2, CURRENT_TIMESTAMP - INTERVAL '3 days', TRUE);
        """)
        
        # Sarah's usage history
        conn.run("""
            INSERT INTO user_product_usage (user_id, product_id, used_at, is_in_routine) VALUES
                -- Sarah: cleanser usage
                (2, 1, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),
                (2, 1, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),
                -- Sarah: vitamin C serum usage
                (2, 2, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),
                (2, 2, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),
                -- Sarah: retinol usage (every 3 days)
                (2, 3, CURRENT_TIMESTAMP - INTERVAL '3 days', TRUE),
                (2, 3, CURRENT_TIMESTAMP - INTERVAL '6 days', TRUE);
        """)
        
        # Lisa's usage history
        conn.run("""
            INSERT INTO user_product_usage (user_id, product_id, used_at, is_in_routine) VALUES
                -- Lisa: cleanser usage (twice daily)
                (3, 1, CURRENT_TIMESTAMP - INTERVAL '12 hours', TRUE),
                (3, 1, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),
                (3, 1, CURRENT_TIMESTAMP - INTERVAL '1 day 12 hours', TRUE),
                (3, 1, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),
                -- Lisa: vitamin C serum usage
                (3, 2, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),
                (3, 2, CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE),
                (3, 2, CURRENT_TIMESTAMP - INTERVAL '3 days', TRUE),
                -- Lisa: retinol usage (intensive)
                (3, 3, CURRENT_TIMESTAMP - INTERVAL '1 day', TRUE),
                (3, 3, CURRENT_TIMESTAMP - INTERVAL '4 days', TRUE),
                (3, 3, CURRENT_TIMESTAMP - INTERVAL '7 days', TRUE);
        """)
               
        print("\n 🎉 Database seeding completed successfully!")
   
    except Exception as e:
        print(f"Error during seeding: {e}")
        raise e
    
    finally:
        close_db(conn)


if __name__ == "__main__":
    seed()