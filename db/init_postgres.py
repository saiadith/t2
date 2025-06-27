import psycopg2
import os

# Database configuration - use environment variables for Docker
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "Rp123456"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "postgres")  # Connect to default database first
}

def init_database():
    # Connect to default database to create our database
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Create database if it doesn't exist
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'customer_events'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE customer_events")
            print("Database 'customer_events' created successfully")
        else:
            print("Database 'customer_events' already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cur.close()
        conn.close()
    
    # Now connect to our database and run the schema
    DB_CONFIG["dbname"] = "customer_events"
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Read and execute the SQL schema as a single script
        with open('db/init_postgres.sql', 'r') as f:
            sql_content = f.read()
        cur.execute(sql_content)
        print("Database schema initialized successfully")
    except Exception as e:
        print(f"Error initializing schema: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database() 