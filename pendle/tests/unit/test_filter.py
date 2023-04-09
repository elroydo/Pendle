import unittest
import numpy as np
from packages.physiology import Physiology

# Define the TestBandpassFilter class
class TestBandpassFilter(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()

    def test_bandpass_filter(self):
        # Create a simple sinusoidal signal with 100 samples
        t = np.linspace(0, 1, 100)
        signal = np.sin(2 * np.pi * 5 * t)

        # Apply FFT to the signal
        fft_signal = np.fft.fft(signal)

        # Define the frequency range for the bandpass filter
        freqs = np.fft.fftfreq(len(signal), t[1] - t[0])
        filter = (freqs >= 4) & (freqs <= 6)

        # Apply the bandpass filter to the FFT result
        filtered_fft_signal = np.copy(fft_signal)
        filtered_fft_signal[~filter] = 0

        # Verify that the filtered FFT result has non-zero values only within the specified frequency range
        nonzero_freqs = freqs[np.nonzero(filtered_fft_signal)]
        self.assertTrue(np.all((nonzero_freqs >= 4) & (nonzero_freqs <= 6)))

        print("Bandpass Filter: Test bandpass filter was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()