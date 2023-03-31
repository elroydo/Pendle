import time
import threading
import numpy as np
import cv2 as cv
from deepface import DeepFace

from .resp_rate import calculate_brpm
from .analyse_emotion import get_dominant_emotion
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
        self.stop_event.set() # Sets event

    # Toggle session
    def toggle_session(self):
        self.session^=True # Switches between true and false

    def run(self):
        print('Monitoring...')

        # Load Haar face shape classifier
        face_cascade = cv.CascadeClassifier('./assets/classifiers/haarcascade_frontalface_default.xml')

        # Initiate video capture
        cap = cv.VideoCapture(0)
        framerate = cap.get(cv.CAP_PROP_FPS) # Frames per second

        # Index and cache variables
        index = 0
        cache_size = 30
        heart_index = 0
        heart_cache_size = 30
        heart_cache = np.zeros((heart_cache_size))
        
        # Gaussian pyramid variables
        face_box = 200
        ROI_gauss = np.zeros((cache_size, face_box//8, face_box//8, 3))

        # Bandpass filter for specific frequencies
        freqs = (1.0*framerate) * np.arange(cache_size) / (1.0 * cache_size) # Create array of evenly spaced frequency values
        
        # # Create boolean array to filter Hz - Sample heart rates in the range of 50-120 bpm
        filter = (freqs >= 0.8) & (freqs <= 2) 

        # Data metrics
        heart_rate = []
        respiration_rate = []
        emotions = []
        session_active = []
        
        # Frame data
        bpm = 0
        brpm = 0
        dominant_emotion = ''
        
        # Miscellaneous
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
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            
            # Face detection parameters
            face = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

            if len(face) > 0:
                (x, y, w, h) = face[0] # Extract face coordinates            

                # Heart rate and breathing
                # Calculate centre and fixed size box around face
                x1, y1 = max(x + w // 2 - face_box // 2, 0), max(y + h // 2 - face_box // 2, 0)
                x2, y2 = min(x1 + face_box, frame.shape[1]), min(y1 + face_box, frame.shape[0])

                # Extract ROI from frame
                face_ROI = frame[y1:y2, x1:x2]

                # Apply gaussian pyramid function to ROI (scaled down image 3 levels)
                down_ROI = face_ROI # Temporary holder
                for _ in range(3):
                    down_ROI = cv.pyrDown(down_ROI) # Downscale frame 

                # Add downscaled gauss frame to index in list
                try:
                    ROI_gauss[index] = down_ROI
                except Exception as e:
                    print(e)

                # Apply Fourier tranform function to downscaled gauss frame 
                fourier = np.fft.fft(ROI_gauss, axis=0) # Compute frequency spectrum along time domain

                # Apply bandpass filter 
                fourier[filter == False] = 0 # Keep specific frequencies

                # Grab heart and respiration rates 
                if index % framerate//2 == 0: # Sampling rate
                    fourier_average = np.real(fourier).mean(axis=(1, 2, 3)) # Store signal averages
                    heart_cache[heart_index] = 60.0 * freqs[np.argmax(fourier_average)] # Multiply max values (hertz) by 60 (seconds)
                    heart_index = (heart_index + 1) % heart_cache_size # Increment circular index

                index = (index + 1) % cache_size # Increment circular index
                
                # Estimate emotions, heart rate, and breathing very second
                if elapsed_time >= 1.0:
                    # Calculate metrics and add to lists
                    bpm = heart_cache.mean() # Average of bpms in heart values cache 
                    brpm = calculate_brpm(bpm) # Ratio heartbeats to breathing
                    dominant_emotion = get_dominant_emotion(frame)
                    
                    # Add data to lists
                    heart_rate.append(bpm) # Add bpm to list
                    respiration_rate.append(brpm) # Add brpm to list
                    emotions.append(dominant_emotion) # Add emotion to list
                    session_active.append(self.session) # Add session state to list
                    
                    # Reset time
                    last_time = current_time

                # Show ROI in window
                try:
                    frame[90:90+25, 10:10+25] = down_ROI # Demo
                    frame[120:120+face_box, 10:10+face_box] = face_ROI * 170
                    frame[y1:y2, x1:x2] = cv.pyrUp(cv.pyrUp(cv.pyrUp(down_ROI))) * 170
                except Exception as e:
                    print(e)

            # Display text with data in frame
            cv.putText(frame, f'BPM: {bpm} | BRPM: {brpm} | Emotion: {dominant_emotion}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv.putText(frame, f'Session: {self.session}', (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # Show frames in a window
            if frame is not None:
                cv.imshow('Janus', frame)
                cv.waitKey(1)
        
        # Zip data making it iterable
        data = list(zip(heart_rate, respiration_rate, emotions, session_active))
        # Save data to database
        self.db.add_data(data)
        # Save data to CSV file
        self.csv_handler.save_data(data)
        
        # Clean up
        cv.destroyAllWindows() # Close all windows
        cap.release() # Close camera capture
        print("Terminating...")