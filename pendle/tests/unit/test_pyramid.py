import unittest
import numpy as np
import cv2 as cv
from packages.physiology import Physiology

# Define the TestGaussianPyramid class
class TestGaussianPyramid(unittest.TestCase):
    def setUp(self):
        self.monitor = Physiology()
        
    def test_build_pyramid(self):
        # Create a test image
        test_image = np.zeros((400, 400, 3), dtype=np.uint8)
        test_image[100:300, 100:300] = 255
        
        # Resize test image to match face_box of 200
        resized_test_image = cv.resize(test_image, (200, 200))
        
        # Apply Gaussian pyramid function to ROI
        down_ROI = self.monitor.build_pyramid(resized_test_image)
        
        # Check that the shape of downsampled ROI is correct
        expected_shape = (25, 25, 3)
        self.assertEqual(down_ROI.shape, expected_shape)
        
        # Check that the sum of pixel values of downsampled ROI is non-zero
        self.assertTrue(down_ROI.sum() > 0)
        
        # Check that the downsampled ROI is of type numpy.ndarray
        self.assertIsInstance(down_ROI, np.ndarray)
        
        print("Gaussian Pyramid: Test build_pyramid was successful.")
        
    def tearDown(self):
        del self.monitor
        
if __name__ == '__main__':
    unittest.main()