import os
import csv
from datetime import datetime
import unittest
from packages.csv_handler import CSVHandler

class TestCSVHandler(unittest.TestCase):
    def setUp(self):
        self.csv_handler = CSVHandler(folder='./tests/test_data')

    def test_save_data(self):
        # Test saving data to CSV file
        data = [
            [0.0, 0.0, 'neutral', False],
            [4.0, 1.0, 'happy', True],
            [8.0, 2.0, 'sad', False]
        ]
        self.csv_handler.save_data(data)
        
        # Test reading data from file
        saved_data = self.csv_handler.get_data()
        self.assertEqual(saved_data, data)
        
         # Print message indicating test success
        print("CSVHandler: Test save_data was successful.")

if __name__ == '__main__':
    unittest.main()