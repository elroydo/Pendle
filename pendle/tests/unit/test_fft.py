import unittest
import numpy as np
from packages.physiology import Physiology

# Define the TestFFT class
class TestFFT(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()

    def test_fft(self):
        # Create a simple sinusoidal signal with 100 samples
        t = np.linspace(0, 1, 100)
        signal = np.sin(2 * np.pi * 5 * t)

        # Apply FFT to the signal
        fft_signal = np.fft.fft(signal)

        # Check if the FFT result has the same length as the input signal
        self.assertEqual(len(fft_signal), len(signal))

        # Check if the FFT result contains complex numbers
        self.assertTrue(np.iscomplex(fft_signal).any())

        print("FFT: Test FFT was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()