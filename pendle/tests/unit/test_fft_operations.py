import unittest
import numpy as np
from packages.physiology import Physiology

# Define the TestFourierOperations class
class TestFourierOperations(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()

    def test_fourier_average(self):
        # Create a sample Fourier transformed data
        np.random.seed(42)
        fourier_data = np.random.rand(10, 5, 5, 3)

        # Calculate the average of the real part of the Fourier transformed data
        fourier_average = np.real(fourier_data).mean(axis=(1, 2, 3))

        # Test the shape of the calculated fourier_average
        self.assertEqual(fourier_average.shape, (10,), "Incorrect fourier_average shape")

        print("Fourier Operations: Test fourier_average was successful.")

    def test_argmax_fourier_average(self):
        # Create a sample Fourier average data
        fourier_average = np.array([1, 5, 3, 2, 8, 7, 4, 0, 6, 9])

        # Get the index of the maximum value in the Fourier average data
        max_index = np.argmax(fourier_average)

        # Test the index of the maximum value
        self.assertEqual(max_index, 9, "Incorrect max_index")

        print("Fourier Operations: Test argmax_fourier_average was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()