import os
import unittest
from unit.test_database import TestPendleDatabase
from unit.test_csv_handler import TestCSVHandler

# create a test suite
test_suite = unittest.TestSuite()

# Add the CSV handler test to the suite
test_suite.addTest(TestCSVHandler('test_save_data'))
# add test cases to the test suite
test_suite.addTest(TestPendleDatabase('test_add_data'))

# run the test suite
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # delete all files in the test_data folder
    for filename in os.listdir('./tests/test_data'):
        filepath = os.path.join('./tests/test_data', filename)
        os.remove(filepath)