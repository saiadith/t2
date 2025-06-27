import psycopg2
import random
from faker import Faker
import os

# Database configuration - use environment variables for Docker
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "Rp123456"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "customer_events")
}

def generate_customers(num_customers=100):
    fake = Faker()
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Clear existing customers
        cur.execute("DELETE FROM customers")
        print("Cleared existing customers")
        
        # Generate new customers
        for i in range(num_customers):
            name = fake.name()
            age = random.randint(18, 80)
            email = fake.email()
            
            cur.execute(
                "INSERT INTO customers (name, age, email) VALUES (%s, %s, %s)",
                (name, age, email)
            )
        
        conn.commit()
        print(f"Generated {num_customers} customers successfully")
        
    except Exception as e:
        print(f"Error generating customers: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    generate_customers() 