import unittest
import numpy as np
from packages.physiology import Physiology

# Define the TestHeartRate class
class TestHeartRate(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()

    def test_calculate_pulse(self):
        # Create a sample frequency (Hertz)
        hertz = 1.5

        # Calculate pulse
        pulse = self.monitor.calculate_pulse(hertz)

        # Test the calculated pulse
        expected_pulse = hertz * 60
        self.assertEqual(pulse, expected_pulse, "Incorrect pulse calculation")

        print("Heart Rate: Test calculate_pulse was successful.")

    def test_calculate_bpm(self):
        # Create a sample heart_cache
        heart_cache = np.array([70, 75, 80, 85, 90])

        # Calculate heart rate
        bpm = self.monitor.calculate_bpm(heart_cache)

        # Test the calculated heart rate
        expected_bpm = np.mean(heart_cache)
        self.assertEqual(bpm, expected_bpm, "Incorrect bpm calculation")

        print("Heart Rate: Test calculate_pulse and calculate_bpm was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()