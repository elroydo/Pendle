import unittest
from unittest import TestCase, mock
import numpy as np
from packages.physiology import Physiology

# Define the TestReadFrames class
class TestReadFrames(TestCase):
    def setUp(self):
        self.monitor = Physiology()
        
    # Use a mock object for the cv2.VideoCapture object
    @mock.patch('cv2.VideoCapture')
    def test_read_frames(self, mock_capture):
        cap = mock_capture.return_value
        cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))

        check, frame = self.monitor.read_frames(cap)

        self.assertTrue(check)
        self.assertIsNotNone(frame)

        print("Reading Frames: Test read_frames was successful.")
        
    def tearDown(self):
        del self.monitor

if __name__ == "__main__":
    unittest.main()