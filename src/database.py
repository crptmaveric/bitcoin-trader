import sqlite3

from logger import Logger

logger = Logger()

def create_database():
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    # Existing table for transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            order_id TEXT,
            invested_amount REAL,
            bitcoin_purchased REAL,
            purchase_price REAL,
            purchase_time TEXT,
            transaction_type TEXT
        )
    ''')

    # Updated table for uninvested balances with new 'investment_date' column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uninvested_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_year TEXT NOT NULL,
            investment_date TEXT NOT NULL,
            uninvested_amount REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def log_transaction(order_id, invested_amount, bitcoin_purchased, purchase_price, purchase_time, transaction_type):
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    # Inserting the new data into the transactions table
    cursor.execute('''
        INSERT INTO transactions (order_id, invested_amount, bitcoin_purchased, purchase_price, purchase_time, transaction_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (order_id, invested_amount, bitcoin_purchased, purchase_price, purchase_time, transaction_type))

    conn.commit()
    conn.close()


def log_uninvested_balance(month_year, investment_date, uninvested_amount):
    conn = sqlite3.connect('trading_app.db')
    try:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO uninvested_balances (month_year, investment_date, uninvested_amount)
            VALUES (?, ?, ?)
        ''', (month_year, investment_date, uninvested_amount))

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_uninvested_balances(month_year=None):
    conn = sqlite3.connect('trading_app.db')
    try:
        cursor = conn.cursor()

        if month_year:
            cursor.execute('''
                SELECT uninvested_amount FROM uninvested_balances WHERE month_year = ?
            ''', (month_year,))
            result = cursor.fetchone()
            return result[0] if result else 0
        else:
            cursor.execute('''
                SELECT SUM(uninvested_amount) FROM uninvested_balances
            ''')
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None
    finally:
        conn.close()
