import os
import unittest
from unit.test_threading import TestThreadFunctionality
from unit.test_camera import TestCamera
from unit.test_read_frame import TestReadFrames
from unit.test_preprocessing import TestPreprocessing
from unit.test_detect_face import TestDetectFace
from unit.test_extract_roi import TestExtractROI
from unit.test_pyramid import TestGaussianPyramid
from unit.test_fft import TestFFT
from unit.test_filter import TestBandpassFilter
from unit.test_fft_operations import TestFourierOperations
from unit.test_heart_rate import TestHeartRate
from unit.test_respiratory_rate import TestBreathingRate
from unit.test_detect_emotion import TestEmotionRecognition
from unit.test_database import TestPendleDatabase
from unit.test_csv_handler import TestCSVHandler

# create a test suite
test_suite = unittest.TestSuite()

# add test cases to the test suite
test_suite.addTest(TestThreadFunctionality('test_thread_methods'))

test_suite.addTest(TestCamera('test_initialise_camera'))
test_suite.addTest(TestReadFrames('test_read_frames'))
test_suite.addTest(TestPreprocessing('test_preprocessing'))
test_suite.addTest(TestDetectFace('test_detect_faces'))
test_suite.addTest(TestExtractROI('test_extract_roi'))

test_suite.addTest(TestGaussianPyramid('test_build_pyramid'))
test_suite.addTest(TestFFT('test_fft'))
test_suite.addTest(TestBandpassFilter('test_bandpass_filter'))
test_suite.addTest(TestFourierOperations('test_fourier_average'))
test_suite.addTest(TestFourierOperations('test_argmax_fourier_average'))

test_suite.addTest(TestHeartRate('test_calculate_pulse'))
test_suite.addTest(TestHeartRate('test_calculate_bpm'))
test_suite.addTest(TestBreathingRate('test_calculate_brpm'))
test_suite.addTest(TestEmotionRecognition('test_emotion_recognition'))

test_suite.addTest(TestPendleDatabase('test_add_data'))
test_suite.addTest(TestCSVHandler('test_save_data'))

# run the test suite
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # delete all files in the test_data folder
    for filename in os.listdir('./tests/test_data'):
        filepath = os.path.join('./tests/test_data', filename)
        os.remove(filepath)