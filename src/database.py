import sqlite3
import time


def create_database():
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    # Updated the transactions table to include new fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            order_id TEXT,
            invested_amount REAL,
            bitcoin_purchased REAL,
            purchase_price REAL,
            purchase_time TEXT
        )
    ''')

    conn.commit()
    conn.close()


def log_transaction(order_id, invested_amount, bitcoin_purchased, purchase_price, purchase_time):
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    # Inserting the new data into the transactions table
    cursor.execute('''
        INSERT INTO transactions (order_id, invested_amount, bitcoin_purchased, purchase_price, purchase_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (order_id, invested_amount, bitcoin_purchased, purchase_price, purchase_time))

    conn.commit()
    conn.close()
