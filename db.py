
import sqlite3, datetime
from utils import hash_password

DB_PATH = "pos.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','caissier')),
        active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS servers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS tables(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER NOT NULL UNIQUE,
        label TEXT,
        active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
        active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER NOT NULL REFERENCES tables(id),
        server_id INTEGER NOT NULL REFERENCES servers(id),
        status TEXT NOT NULL CHECK(status IN ('open','closed')) DEFAULT 'open',
        created_at TEXT NOT NULL,
        closed_at TEXT,
        total REAL NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products(id),
        qty INTEGER NOT NULL,
        price REAL NOT NULL
    );
    """)

    # seed default users
    c.execute("SELECT COUNT(*) AS n FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                  ("admin", hash_password("admin123"), "admin"))
        c.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                  ("caissier", hash_password("caissier123"), "caissier"))

    # seed tables
    c.execute("SELECT COUNT(*) AS n FROM tables")
    if c.fetchone()[0] == 0:
        for num in range(1, 11):
            c.execute("INSERT INTO tables(number,label) VALUES(?,?)", (num, f"Table {num}"))

    # seed servers
    c.execute("SELECT COUNT(*) AS n FROM servers")
    if c.fetchone()[0] == 0:
        for name in ["Alice", "Bob", "Chantal"]:
            c.execute("INSERT INTO servers(name) VALUES(?)", (name,))

    # seed categories/products
    c.execute("SELECT COUNT(*) AS n FROM categories")
    if c.fetchone()[0] == 0:
        cats = ["Boissons", "Snacks", "Plats"]
        for cat in cats:
            c.execute("INSERT INTO categories(name) VALUES(?)", (cat,))
        conn.commit()
        # map names to ids
        cat_ids = {row[1]: row[0] for row in conn.execute("SELECT id,name FROM categories")}
        demo_products = [
            ("Coca-Cola 33cl", 1.50, "Boissons"),
            ("Eau 50cl", 1.00, "Boissons"),
            ("Jus d'orange", 2.00, "Boissons"),
            ("Chips", 1.20, "Snacks"),
            ("Arachides", 1.00, "Snacks"),
            ("Sandwich", 3.50, "Snacks"),
            ("Poulet braisé", 6.00, "Plats"),
            ("Poisson", 7.00, "Plats"),
            ("Frites", 2.00, "Plats"),
        ]
        for name, price, cat in demo_products:
            c.execute("INSERT INTO products(name,price,category_id) VALUES(?,?,?)",
                      (name, price, cat_ids[cat]))

    conn.commit()
    conn.close()

def auth_user(username, password):
    conn = get_conn()
    row = conn.execute("SELECT id, username, password_hash, role, active FROM users WHERE username=? AND active=1", (username,)).fetchone()
    if not row:
        conn.close()
        return None
    ok = (row[2] == hash_password(password))
    user = {"id": row[0], "username": row[1], "role": row[3], "active": row[4]}
    conn.close()
    return user if ok else None
