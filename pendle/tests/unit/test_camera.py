import unittest
from unittest import TestCase, mock
import cv2
from packages.physiology import Physiology

# Define the TestCamera class
class TestCamera(TestCase):
    def setUp(self):
        self.monitor = Physiology()
        
    # Use a mock object for the cv2.VideoCapture object
    @mock.patch('cv2.VideoCapture')
    def test_initialise_camera(self, mock_capture):
        cap = self.monitor.initialise_camera()
        self.assertTrue(cap.isOpened())

        print("Camera Initialisation: Test initialise_camera was successful.")
        
    def tearDown(self):
        del self.monitor
        
if __name__ == "__main__":
    unittest.main()