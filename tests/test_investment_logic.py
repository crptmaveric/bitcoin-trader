import unittest
from src.investment_logic import calculate_investment_amount, get_fear_and_greed_index

class TestInvestmentLogic(unittest.TestCase):

    def test_calculate_investment_amount(self):
        self.assertEqual(calculate_investment_amount(10, 1000, 4), 375.0)
        self.assertEqual(calculate_investment_amount(50, 1000, 4), 250.0)
        # Doplniť ďalšie prípady podľa potreby

    def test_get_fear_and_greed_index(self):
        index_value = get_fear_and_greed_index()
        self.assertIsInstance(index_value, int)
        self.assertTrue(0 <= index_value <= 100)

if __name__ == '__main__':
    unittest.main()
