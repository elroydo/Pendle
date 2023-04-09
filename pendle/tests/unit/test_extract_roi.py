import unittest
import cv2
from packages.physiology import Physiology

# Define the TestExtractROI class
class TestExtractROI(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()
        # Load Haar face shape classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def test_extract_roi(self):
        # Load sample image
        test_image = cv2.imread(r'\\mac\Home\Documents\GitHub\Pendle\pendle\tests\unit\test.png')
        # Convert to grayscale
        gray_img = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        # Detect faces in grayscale image
        faces = self.face_cascade.detectMultiScale(gray_img, 1.3, 5)

        # Extract ROI if faces detected
        if len(faces) > 0:
            # Get first detected face
            face = faces[0]
            # Extract ROI and coordinates
            roi, x1, y1, x2, y2 = self.monitor.extract_roi(test_image, [face], 200)

            # Verify ROI dimensions
            self.assertEqual(roi.shape, (200, 200, 3))
            
            print("Detect Face: Test extract_roi was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()