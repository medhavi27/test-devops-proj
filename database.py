import os
import time
import psycopg2

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL", "postgresql://admin:secretpass@menu-db:5432/restaurant_db")
    return psycopg2.connect(db_url)

def init_db():
    print("--> FLASK IS WAITING FOR DATABASE TO BE READY...")
    conn = None
    retries = 5
    
    while retries > 0:
        try:
            conn = get_db_connection()
            break
        except psycopg2.OperationalError:
            retries -= 1
            print(f"--> Database not ready yet ({retries} retries left). Waiting 2 seconds...")
            time.sleep(2)
            
    if not conn:
        print("--> ERROR: Could not connect to the database after multiple attempts.")
        raise Exception("Database connection failed permanently.")

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price NUMERIC(5, 2) NOT NULL
        );
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM menu;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO menu (name, price) VALUES ('Classic Burger', 12.99);")
        cursor.execute("INSERT INTO menu (name, price) VALUES ('Truffle Fries', 5.50);")
        cursor.execute("INSERT INTO menu (name, price) VALUES ('Iced Latte', 4.25);")
        print("--> DATABASE INITIALIZED AND SEEDED SUCCESSFULLY!")
        
    conn.commit()
    cursor.close()
    conn.close()