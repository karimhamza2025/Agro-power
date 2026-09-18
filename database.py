import sqlite3

connection = sqlite3.connect("agro_power.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS parties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    party_type TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    notes TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    notes TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT NOT NULL,
    permission_number TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    party_id INTEGER NOT NULL,
    driver_name TEXT,
    car_number TEXT,
    responsible_person TEXT,
    notes TEXT,
    FOREIGN KEY (party_id) REFERENCES parties(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS transaction_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    value REAL NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_date TEXT NOT NULL,
    party_id INTEGER NOT NULL,
    payment_type TEXT NOT NULL,
    amount REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY (party_id) REFERENCES parties(id)
)
""")
connection.commit()
connection.close()

print("Parties table created successfully!")


