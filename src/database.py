import sqlite3
import datetime
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

    # New table for tracking the last purchase date
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS last_purchase (
            id INTEGER PRIMARY KEY,
            last_purchase_date TEXT
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


# New functions to manage the last purchase date
def get_last_purchase_date():
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT last_purchase_date FROM last_purchase ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def update_last_purchase_date(date):
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO last_purchase (last_purchase_date) VALUES (?)', (date,))
    conn.commit()
    conn.close()


def get_average_buy_price():
    # Connect to the database
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    # Execute a query to calculate the weighted average
    cursor.execute('''
        SELECT SUM(bitcoin_purchased * purchase_price) / SUM(bitcoin_purchased)
        FROM transactions
    ''')

    # Fetch the result and close the connection
    weighted_average_price = cursor.fetchone()[0]
    conn.close()

    # Format the result to two decimal places
    if weighted_average_price is not None:
        weighted_average_price = "{:.2f}".format(weighted_average_price)

    return weighted_average_price


def get_last_transaction_date():
    """Retrieves the date of the most recent transaction from the database."""
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT purchase_time FROM transactions ORDER BY purchase_time DESC LIMIT 1
    ''')
    last_transaction_time = cursor.fetchone()
    conn.close()

    if last_transaction_time is None:
        return None

    # Odstránenie 'Z' a prevod na datetime objekt
    isoformat_time = last_transaction_time[0].replace('Z', '')
    datetime_obj = datetime.datetime.fromisoformat(isoformat_time)
    formatted_date = datetime_obj.strftime('%d.%m.%Y')

    return formatted_date

