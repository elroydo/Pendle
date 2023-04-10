import datetime
import time
import threading
import numpy as np
import cv2 as cv
from deepface import DeepFace

# Import packages
from .plot_utils import plot_signals
from .csv_handler import CSVHandler
from .database import PendleDatabase

class Physiology(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True) # Kill thread if main is closed
        self.stop_event = threading.Event() # Initialise threading event
        self.db = PendleDatabase()
        self.csv_handler = CSVHandler()
        self.session = False
        
        # Load Haar face shape classifier
        self.face_cascade = cv.CascadeClassifier('./assets/classifiers/haarcascade_frontalface_default.xml')

        # Initiate video capture
        self.cap = self.initialise_camera()
        self.framerate = self.cap.get(cv.CAP_PROP_FPS) # Frames per second

        # Index and cache variables
        self.index = 0
        self.cache_size = 100
        self.heart_index = 0
        self.heart_cache_size = 15
        self.heart_cache = np.zeros((self.heart_cache_size))

        # Gaussian pyramid variables
        self.face_box = 200
        self.ROI_gauss = np.zeros((self.cache_size, self.face_box//8, self.face_box//8, 3))

        # Create array of evenly spaced frequency values
        self.freqs = (1.0*self.framerate//2) * np.arange(self.cache_size) / (1.0 * self.cache_size)

        # Bandpass filter for specific frequencies - Keep heart rates in the range of 50-120 bpm
        self.filter = (self.freqs >= 0.8) & (self.freqs <= 2)

        # Data metrics
        self.timestamp_list = []
        self.heart_rate = []
        self.respiration_rate = []
        self.emotions = []
        self.session_active = []

        # Frame data
        self.bpm = 0
        self.brpm = 0
        self.dominant_emotion = ''

        # Miscellaneous
        self.start_time = time.time()
        self.last_time = time.time()
    
    # Stop thread
    def stop(self):
        self.stop_event.set()

    # Toggle session
    def toggle_session(self):
        self.session ^= True
    
    # Initialise first detected camera device
    def initialise_camera(self):
        for i in range(10):
            cap = cv.VideoCapture(i)
            if cap.isOpened():
                return cap
        if not cap.isOpened():
            print("Camera inaccessible...")
        return cap
    
    # Read frames from camera
    def read_frames(self, capture):
        check, frame = capture.read()
        if not check:
            print("Missing frames...")
            return check, None
        return check, frame
    
    # Enhance frames
    def preprocessing(self, frame):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        alpha = cv.convertScaleAbs(frame, alpha=1.7, beta=0)
        return gray, alpha
    
    # Face detection & tracking; return first face
    def detect_faces(self, grey_frame, classifier):
        faces = classifier.detectMultiScale(grey_frame, 1.3, 5)
        if len(faces) >= 1:
            face = faces[:1]
            return face
        return []
    
    # Extract ROI and coordinates
    def extract_roi(self, frame, face, face_box):
        # Extract first face coordinates
        (x, y, w, h) = face[0]
        
        # Calculate centre and fixed size box around face
        x1, y1 = max(x + w // 2 - face_box // 2,0), max(y + h // 2 - face_box // 2, 0)
        x2, y2 = min(x1 + face_box, frame.shape[1]), min(y1 + face_box, frame.shape[0])
        
        return frame[y1:y2, x1:x2], x1, y1, x2, y2
    
    # Apply gaussian pyramid function to ROI (scaled down image 3 levels)
    def build_pyramid(self, ROI):
        down_ROI = ROI
        for _ in range(3):
            down_ROI = cv.pyrDown(down_ROI)
        return down_ROI
    
    # Calculate pulse
    def calculate_pulse(self, hertz):
        return hertz * 60
    
    # Calculate heart rate
    def calculate_bpm(self, cache):
        return cache.mean()
        
    # Ratio heartbeats to breathing
    def calculate_brpm(self, bpm):
        return bpm // 4
        
    # Emotion recognition using Deepface
    def get_dominant_emotion(self, alpha_frame):
        try:
            emotion = DeepFace.analyze(alpha_frame, actions=['emotion'], silent=True, enforce_detection=False)
            dominant_emotion = emotion[0]['dominant_emotion']
            return dominant_emotion
        except Exception as e:
            print('Emotion could not be detected.')
            return None

    def run(self):
        print('Monitoring...')

        # Check stopping thread condition
        while not self.stop_event.is_set():
            # Timing variables
            current_time = time.time()
            elapsed_time = current_time - self.last_time

            # Capture each frame
            check, frame = self.read_frames(self.cap)

            # Pre-processing; enhance frames
            grey_frame, alpha_frame = self.preprocessing(frame)

            # Face detection & tracking parameters
            face = self.detect_faces(grey_frame, self.face_cascade)

            if len(face) > 0:
                # Extract ROI & coordinates from frame
                face_ROI, x1, y1, x2, y2 = self.extract_roi(frame, face, self.face_box)

                # Build pyramid and add downscaled frame to index in list
                try:
                    ROI_pyramid = self.build_pyramid(face_ROI)
                    self.ROI_gauss[self.index] = ROI_pyramid
                except Exception as e:
                    print(e)

                # Apply Fourier tranform function to downscaled frame
                fourier = np.fft.fft(self.ROI_gauss, axis=0)

                # Apply bandpass filter keeping specific frequencies
                fourier[self.filter == False] = 0

                # Grab physiological features
                if self.index % self.framerate//2 == 0: # Sampling rate
                    # Compute & store signal averages from top-down
                    fourier_average = np.real(fourier).mean(axis=(1, 2, 3))
                    # Multiply corresponding frequency (Hertz) by 60 (seconds)
                    self.heart_cache[self.heart_index] = self.calculate_pulse(self.freqs[np.argmax(fourier_average)])
                    # Increment circular index
                    self.heart_index = (self.heart_index + 1) % self.heart_cache_size
                # Increment circular index
                self.index = (self.index + 1) % self.cache_size

                # Calculate & store emotions, heart rate, and breathing every second
                if elapsed_time >= 1.0:
                    self.timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    self.bpm = self.calculate_bpm(self.heart_cache.mean()) # Heart rate
                    self.brpm = self.calculate_brpm(self.bpm) # Respiration rate
                    self.dominant_emotion = self.get_dominant_emotion(alpha_frame) # Emotion

                    # Add data to lists
                    self.timestamp_list.append(self.timestamp)
                    self.heart_rate.append(self.bpm)
                    self.respiration_rate.append(self.brpm) 
                    self.emotions.append(self.dominant_emotion)
                    self.session_active.append(self.session) # Session state

                    # Reset time
                    self.last_time = current_time

                # Show ROI in window; demo
                try:
                    frame[120:120+25, 10:10+25] = ROI_pyramid
                    frame[150:150+self.face_box, 10:10+self.face_box] = face_ROI * 170
                    frame[y1:y2, x1:x2] = cv.pyrUp(cv.pyrUp(cv.pyrUp(ROI_pyramid))) * 170 + frame[y1:y2, x1:x2]
                except Exception as e:
                    print(e)

            # Display text with data in frame
            cv.putText(frame, f'Elapsed time: {int(time.time() - self.start_time)}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            cv.putText(frame, f'BPM: {self.bpm} | BRPM: {self.brpm} | Emotion: {self.dominant_emotion}', (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            cv.putText(frame, f'Session: {self.session}', (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

            # Show frames in a window
            if frame is not None:
                cv.imshow('Janus', frame)
                cv.waitKey(1)
    
        print(f'List lengths: 42, 42, 42, 10, 42')
        # Zip & save iterable data
        data = list(zip(self.timestamp_list, self.heart_rate, self.respiration_rate, self.emotions, self.session_active))
        self.db.add_data(data)
        self.csv_handler.save_data(data)

        # Clean up
        cv.destroyAllWindows()
        self.cap.release()
        print("Terminating...")