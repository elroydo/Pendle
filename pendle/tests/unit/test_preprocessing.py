import unittest
import cv2 as cv
from unittest import TestCase, mock
from packages.physiology import Physiology

# Define the TestPreprocessing class
class TestPreprocessing(TestCase):
    def setUp(self):
        self.monitor = Physiology()
        
    def test_preprocessing(self):
        # create mock frame
        frame = mock.MagicMock()
        # create mock for cvtColor and convertScaleAbs
        mock_cvtColor = mock.Mock()
        mock_convertScaleAbs = mock.Mock()

        # patch the cv2 module to return the mocks
        with mock.patch("cv2.cvtColor", mock_cvtColor), \
            mock.patch("cv2.convertScaleAbs", mock_convertScaleAbs):
            gray, alpha = self.monitor.preprocessing(frame)

        mock_cvtColor.assert_called_once_with(frame, cv.COLOR_BGR2GRAY)
        mock_convertScaleAbs.assert_called_once_with(frame, alpha=1.7, beta=0)

        self.assertIsNotNone(gray)
        self.assertIsNotNone(alpha)

        print("Preprocessing: Test preprocessing was successful.")
        
    def tearDown(self):
        del self.monitor

if __name__ == "__main__":
    unittest.main()