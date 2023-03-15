import os
import time
import datetime
import threading
import numpy as np
import csv
import cv2 as cv
from deepface import DeepFace

class Physiology(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True) #Kill thread if main is closed
        self.stop_event = threading.Event() #Initialise threading event
        self.session = False
    
    #Stop thread
    def stop(self):
        self.stop_event.set() #Sets event

    #Toggle session
    def toggle_session(self):
        self.session^=True #Switches between true and false

    #CSV jazz
    def save_data(self, data):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data_{timestamp}.csv"
        folder = 'data/'
        filepath = os.path.join(folder, filename) #Get full path

        #Create data folder if it doesn't exist
        if not os.path.exists(folder):
                os.makedirs(folder)
        
        #Create data file if it doesn't exist
        if not os.path.isfile(filepath): #Check if file exists 
            with open(filepath, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['bpm', 'brpm', 'emotions', 'session']) #Write headers
                for metric in data:
                    writer.writerow(metric) #Write data to file
            print(f'Data written to {filepath}.')
        else:
            print(f'{filepath} already exists.')

    def run(self):
        print('Monitoring...')

        #Load Haar face shape classifier
        face_cascade = cv.CascadeClassifier('./assets/classifiers/haarcascade_frontalface_default.xml')

        #Initiate video capture
        cap = cv.VideoCapture(0)
        cap.set(3, 600) #Set camera resolution - height
        cap.set(4, 600) #Set camera resolution - width
        framerate = cap.get(cv.CAP_PROP_FPS)  #Frames per second

        #Index and cache variables
        index = 0
        cache_size = 150
        heart_index = 0
        heart_cache_size = 15
        heart_calc_freq = framerate//2
        heart_cache = np.zeros((heart_cache_size))
        
        #Gaussian pyramid variables
        scale = 3
        face_box = 200
        ROI_gauss = np.zeros((cache_size, face_box//8, face_box//8, 3))

        #Fourier jazz
        fourier_average = np.zeros((cache_size))

        #Bandpass filter for specific frequencies
        min_freq, max_freq = 0.8, 2 #Hz - Sample heart rates in the range of 50-120 bpm
        freqs = (1.0*framerate) * np.arange(cache_size) / (1.0 * cache_size) #Create array of evenly spaced frequency values
        filter = (freqs >= min_freq) & (freqs <= max_freq) #Create boolean array to filter frequency values

        #CSV data metrics
        heart_rate = []
        respiration_rate = []
        emotions = []
        session_active = []
        
        #Frame data
        last_time = time.time()
        bpm = 0
        brpm = 0
        dominant_emotion = ''

        #Check if camera is accessible
        if not cap.isOpened():
            print("Camera inaccessible...")
        
        #Check stopping thread condition
        while not self.stop_event.is_set():
            #Timing variables
            current_time = time.time()
            elapsed_time = current_time - last_time
            
            #Capture each frame
            check, frame = cap.read()
            
            #Set check to true if frame is read correctly
            if not check:
                print("Missing frames, ending capture...")
                break
            
            #Operations on the frame
            grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) #Set frame colour to grey
            duality = cv.convertScaleAbs(frame, alpha=1.7, beta=0) #Enhance image for facial feature processing

            #Face detection parameters
            face = face_cascade.detectMultiScale(grey, 1.3, 5)

            if len(face) > 0:
                #Left, top, right, bottom
                (x, y, w, h) = face[0] #Extract face coordinates            

                #Heart rate and breathing
                #Calculate centre and fixed size box around face
                x_center = x + w // 2
                y_center = y + h // 2
                half_face_box = face_box // 2
                x1 = max(x_center - half_face_box, 0)
                y1 = max(y_center - half_face_box, 0)
                x2 = min(x_center + half_face_box, frame.shape[1])
                y2 = min(y_center + half_face_box, frame.shape[0])
                
                #Display boxes around detected face
                cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

                #Extract ROI from frame
                face_ROI = frame[y1:y2, x1:x2]

                #Apply gaussian pyramid function to ROI (scaled down image 3 levels)
                down_ROI = face_ROI #Temporary holder
                pyramid = [down_ROI]
                for _ in range(scale):
                    down = cv.pyrDown(down_ROI) #Downscale frame 
                    down_ROI = down #Assign downscaled frame
                    pyramid.append(down_ROI) #Add to list

                #Add downscaled gauss frame to index in list
                try:
                    ROI_gauss[index] = pyramid[scale]
                except Exception as e:
                    print(e)

                #Apply Fourier tranform function to downscaled gauss frame 
                fourier = np.fft.fft(ROI_gauss, axis=0) #Compute frequency spectrum along time domain

                #Apply bandpass filter 
                fourier[filter == False] = 0 #Keep specific frequencies

                #Grab heart and respiration rates 
                if index % heart_calc_freq == 0: #Sampling rate
                    for _ in range(cache_size): #Iterate through cache_size
                        fourier_average[_] = np.real(fourier[_]).mean() #Store signal averages
                    heart_cache[heart_index] = 60.0 * freqs[np.argmax(fourier_average)] #Multiply max values (hertz) by 60 (seconds)
                    heart_index = (heart_index + 1) % heart_cache_size #Increment circular index

                index = (index + 1) % cache_size #Increment circular index
                
                #Every second
                if elapsed_time >= 1.0:
                    #Emotion recognition using Deepface
                    try:
                        emotion = DeepFace.analyze(duality, actions=['emotion'], silent=True) #Emotional analysis
                        dominant_emotion = emotion[0]['dominant_emotion']
                    except Exception as e:
                        print(e) #Display error
                    
                    #Calculate metrics and add to lists
                    bpm = heart_cache.mean() #Average of bpms in heart values cache 
                    brpm = bpm//4 #Ratio heartbeats to breathing
                    
                    heart_rate.append(bpm) #Add bpm to list
                    respiration_rate.append(brpm) #Add brpm to list
                    emotions.append(dominant_emotion) #Add emotion to list
                    session_active.append(self.session) #Add session state to list
                    
                    #Reset time
                    last_time = current_time

                #Show ROI in window
                try:
                    frame[y1:y2, x1:x2] = cv.pyrUp(cv.pyrDown(face_ROI)) * 170
                except Exception as e:
                    print(e)

            cv.putText(frame, f'BPM: {bpm}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) #Display bpm
            cv.putText(frame, f'BRPM: {brpm}', (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) #Display brpm
            cv.putText(frame, f'Emotion: {dominant_emotion}', (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) #Display emotion
            cv.putText(frame, f'Session: {self.session}', (10, 120), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) #Display session state

            #Show frames in a window
            if frame is not None:
                cv.imshow('Janus', frame)
                cv.waitKey(1)
        
        #Zip data making it iterable
        data = zip(heart_rate, respiration_rate, emotions, session_active)
        #Save data to CSV file
        self.save_data(data)
        
        #Clean up
        cv.destroyAllWindows() #Close all windows
        cap.release() #Close camera capture
        print("Terminating...")