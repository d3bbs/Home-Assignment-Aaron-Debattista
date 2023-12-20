import sqlite3

def create_database():
    # Connect to the database (create a new one if it doesn't exist)
    conn = sqlite3.connect('router_database.db')
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Create a table to store router data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS routers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ip_address TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
create_database()
