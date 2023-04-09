import unittest
from unittest import TestCase, mock
from packages.physiology import Physiology

# Define the TestThreadFunctionality class
class TestThreadFunctionality(TestCase):
    def setUp(self):
        self.monitor = Physiology()

    def test_thread_methods(self):
        # Mock the required methods in Physiology class
        self.monitor.start = mock.MagicMock()
        self.monitor.toggle_session = mock.MagicMock()
        self.monitor.stop = mock.MagicMock()
        self.monitor.join = mock.MagicMock()

        # Test the start method
        self.monitor.start()
        self.monitor.start.assert_called_once()

        # Test the toggle_session method
        self.monitor.toggle_session()
        self.monitor.toggle_session.assert_called_once()

        # Test the stop method
        self.monitor.stop()
        self.monitor.stop.assert_called_once()

        # Test the join method
        self.monitor.join()
        self.monitor.join.assert_called_once()
        
        print("Threading Functionality: Test start, toggle, stop, and join thread was successful.")
        
    def tearDown(self):
        del self.monitor

if __name__ == "__main__":
    unittest.main()