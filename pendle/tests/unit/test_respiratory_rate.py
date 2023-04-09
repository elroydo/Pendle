import unittest
from packages.physiology import Physiology

# Define the TestBreathingRate class
class TestBreathingRate(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()

    def test_calculate_brpm(self):
        # Create a sample heart rate (BPM)
        bpm = 80

        # Calculate breathing rate
        brpm = self.monitor.calculate_brpm(bpm)

        # Test the calculated breathing rate
        expected_brpm = bpm // 4
        self.assertEqual(brpm, expected_brpm, "Incorrect breathing rate calculation")

        print("Breathing Rate: Test calculate_brpm was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()