import os
import unittest
from packages.database import PendleDatabase

# Define the TestPendleDatabase class
class TestPendleDatabase(unittest.TestCase):
    # Create a new instance of database before each test
    def setUp(self):
        self.db = PendleDatabase(db_name='test', folder='./test_data')

    # Test adding data to the database
    def test_add_data(self):
        data = [
            ['11:11:11', 0.0, 0.0, 'neutral', False],
            ['11:11:12', 4.0, 1.0, 'happy', True],
            ['11:11:13', 8.0, 2.0, 'angry', False],
        ]
        self.db.add_data(data)

        # Retrieve the data from the database and check that it matches the input data
        result = self.db.get_data()
        self.assertEqual(result, [('11:11:11', 0.0, 0.0, 'neutral', False), ('11:11:12', 4.0, 1.0, 'happy', True), ('11:11:13', 8.0, 2.0, 'angry', False)])
        
        # Print message indicating test success
        print("Database: Test add_data was successful.")

if __name__ == '__main__':
    unittest.main()