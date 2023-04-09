import unittest
import cv2
from packages.physiology import Physiology

# Define the TestDetectFace class
class TestDetectFace(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()
        # Load Haar face shape classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def test_detect_faces(self):
        # Load sample image
        test_image = cv2.imread(r'\\mac\Home\Documents\GitHub\Pendle\pendle\tests\unit\test.png')
        # Preprocessing
        grey_frame = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        # Detect faces in grayscale image
        faces = self.monitor.detect_faces(grey_frame, self.face_cascade)
        
        # Test number of detected faces
        self.assertTrue(len(faces) > 0)
        self.assertEqual(len(faces), 1)
        
        print("Detect Face: Test detect_face was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()