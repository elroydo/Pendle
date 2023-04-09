import unittest
import cv2
from packages.physiology import Physiology

# Define the TestEmotionRecognition class
class TestEmotionRecognition(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()

    def test_emotion_recognition(self):
        # Load sample image
        test_image = cv2.imread(r'\\mac\Home\Documents\GitHub\Pendle\pendle\tests\unit\test.png')

        # Preprocessing
        alpha_frame = cv2.convertScaleAbs(test_image, alpha=1.7, beta=0)

        # Get the dominant emotion using the DeepFace library
        detected_emotion = self.monitor.get_dominant_emotion(alpha_frame)

        # Check if the detected emotion is not None
        self.assertIsNotNone(detected_emotion)

        # Check if the detected emotion matches the expected emotion
        self.assertEqual(detected_emotion, 'neutral')

        print("Emotion Recognition: Test emotion recognition was successful.")

    def tearDown(self):
        del self.monitor

if __name__ == '__main__':
    unittest.main()