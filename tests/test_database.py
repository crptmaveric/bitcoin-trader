import unittest
import sqlite3
from src.database import create_database, log_transaction

class TestDatabase(unittest.TestCase):
    def setUp(self):
        create_database()
        self.conn = sqlite3.connect('trading_app.db')
        self.cursor = self.conn.cursor()

    def test_log_transaction(self):
        test_amount = 100
        test_price = 50000
        test_index_value = 50
        log_transaction(test_amount, test_price, test_index_value)
        self.cursor.execute("SELECT amount, price, index_value FROM transactions ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        self.assertEqual(result, (test_amount, test_price, test_index_value))

    def tearDown(self):
        self.conn.execute('DELETE FROM transactions')
        self.conn.commit()
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
