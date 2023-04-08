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

    # Stop thread
    def stop(self):
        self.stop_event.set()

    # Toggle session
    def toggle_session(self):
        self.session ^= True
    
    # Enhance frames
    def preprocessing(self, frame):
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        alpha = cv.convertScaleAbs(frame, alpha=1.7, beta=0)
        return gray, alpha
    
    # Apply gaussian pyramid function to ROI (scaled down image 3 levels)
    def build_pyramid(self, ROI):
        down_ROI = ROI
        for _ in range(3):
            down_ROI = cv.pyrDown(down_ROI)
        return down_ROI
    
    def calculate_pulse(self, hertz):
        return hertz * 60
    
    def calculate_bpm(self, cache):
        return cache.mean()
        
    # Ratio heartbeats to breathing
    def calculate_brpm(self, bpm):
        return bpm // 4
        
    # Emotion recognition using Deepface
    def get_dominant_emotion(self, alpha_frame):
        try:
            emotion = DeepFace.analyze(alpha_frame, actions=['emotion'], silent=True)
            dominant_emotion = emotion[0]['dominant_emotion']
            return dominant_emotion
        except Exception as e:
            print(e)
            return None

    def run(self):
        print('Monitoring...')

        # Load Haar face shape classifier
        face_cascade = cv.CascadeClassifier('./assets/classifiers/haarcascade_frontalface_default.xml')

        # Initiate video capture
        cap = cv.VideoCapture(0)
        framerate = cap.get(cv.CAP_PROP_FPS) # Frames per second

        # Index and cache variables
        index = 0
        cache_size = 100
        heart_index = 0
        heart_cache_size = 15
        heart_cache = np.zeros((heart_cache_size))

        # Gaussian pyramid variables
        face_box = 200
        ROI_gauss = np.zeros((cache_size, face_box//8, face_box//8, 3))

        # Create array of evenly spaced frequency values
        freqs = (1.0*framerate//2) * np.arange(cache_size) / (1.0 * cache_size)

        # Bandpass filter for specific frequencies - Keep heart rates in the range of 50-120 bpm
        filter = (freqs >= 0.8) & (freqs <= 2)

        # Data metrics
        timestamp_list = []
        heart_rate = []
        respiration_rate = []
        emotions = []
        session_active = []

        # Frame data
        bpm = 0
        brpm = 0
        dominant_emotion = ''

        # Miscellaneous
        start_time = time.time()
        last_time = time.time()

        # Check if camera is accessible
        if not cap.isOpened():
            print("Camera inaccessible...")

        # Check stopping thread condition
        while not self.stop_event.is_set():
            # Timing variables
            current_time = time.time()
            elapsed_time = current_time - last_time

            # Capture each frame
            check, frame = cap.read()

            # Set check to true if frame is read correctly
            if not check:
                print("Missing frames, ending capture...")
                break

            # Pre-processing; enhance frames
            gray_frame, alpha_frame = self.preprocessing(frame)

            # Face detection parameters
            face = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

            if len(face) > 0:
                # Extract face coordinates
                (x, y, w, h) = face[0]

                # Calculate centre and fixed size box around face
                x1, y1 = max(x + w // 2 - face_box // 2,0), max(y + h // 2 - face_box // 2, 0)
                x2, y2 = min(x1 + face_box, frame.shape[1]), min(y1 + face_box, frame.shape[0])

                # Extract ROI from frame
                face_ROI = frame[y1:y2, x1:x2]

                # Build pyramid and add downscaled frame to index in list
                try:
                    ROI_pyramid = self.build_pyramid(face_ROI)
                    ROI_gauss[index] = ROI_pyramid
                except Exception as e:
                    print(e)

                # Apply Fourier tranform function to downscaled frame
                fourier = np.fft.fft(ROI_gauss, axis=0)

                # Apply bandpass filter keeping specific frequencies
                fourier[filter == False] = 0

                # Grab heart and respiration rates
                if index % framerate//2 == 0: # Sampling rate
                    # Compute & store signal averages from top-down
                    fourier_average = np.real(fourier).mean(axis=(1, 2, 3))
                    # Multiply corresponding frequency (Hertz) by 60 (seconds)
                    heart_cache[heart_index] = self.calculate_pulse(freqs[np.argmax(fourier_average)])
                    # Increment circular index
                    heart_index = (heart_index + 1) % heart_cache_size
                # Increment circular index
                index = (index + 1) % cache_size

                # Calculate & store emotions, heart rate, and breathing every second
                if elapsed_time >= 1.0:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    bpm = self.calculate_bpm(heart_cache.mean()) # Heart rate
                    brpm = self.calculate_brpm(bpm) # Respiration rate
                    dominant_emotion = self.get_dominant_emotion(alpha_frame) # Emotion

                    # Add data to lists
                    timestamp_list.append(timestamp)
                    heart_rate.append(bpm)
                    respiration_rate.append(brpm) 
                    emotions.append(dominant_emotion)
                    session_active.append(self.session) # Session state

                    # Reset time
                    last_time = current_time

                # Show ROI in window; demo
                try:
                    frame[120:120+25, 10:10+25] = ROI_pyramid
                    frame[150:150+face_box, 10:10+face_box] = face_ROI * 170
                    frame[y1:y2, x1:x2] = cv.pyrUp(cv.pyrUp(cv.pyrUp(ROI_pyramid))) * 170 + frame[y1:y2, x1:x2]
                except Exception as e:
                    print(e)

            # Display text with data in frame
            cv.putText(frame, f'Elapsed time: {int(time.time() - start_time)}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            cv.putText(frame, f'BPM: {bpm} | BRPM: {brpm} | Emotion: {dominant_emotion}', (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            cv.putText(frame, f'Session: {self.session}', (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

            # Show frames in a window
            if frame is not None:
                cv.imshow('Janus', frame)
                cv.waitKey(1)

        # Zip & save iterable data
        data = list(zip(timestamp_list, heart_rate, respiration_rate, emotions, session_active))
        self.db.add_data(data)
        self.csv_handler.save_data(data)

        # Clean up
        cv.destroyAllWindows()
        cap.release()
        print("Terminating...")