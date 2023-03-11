import os
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
    
    #Stop thread
    def stop(self):
        self.stop_event.set()

    #CSV jazz
    def save_data(self, data):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data_{timestamp}.csv"
        folder = 'data/'
        filepath = os.path.join(folder, filename) #Get full path

        if not os.path.isfile(filepath): #Check if file exists
            with open(filepath, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['bpm', 'brpm', 'emotions']) #Write headers
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
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 640) #Set camera resolution - height
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 480) #Set camera resolution - width
        framerate = cap.get(cv.CAP_PROP_FPS)  #Frames per second

        #Face variables
        face_box = 200

        #Index and cache variables
        index = 0
        cache_size = 100
        heart_index = 0
        heart_cahce_size = 30
        heart_calc_freq = 30
        heart_cache = np.zeros((heart_cahce_size))
        
        #Gaussian pyramid variables
        scale = 3
        ROI_gauss = np.zeros((cache_size, face_box//8, face_box//8, 3))

        #Fourier jazz
        min_freq = 1.0
        max_freq = 1.8
        fourier_average = np.zeros((cache_size))

        #Bandpass filter for specific frequencies
        freqs = (1.0*framerate) * np.arange(cache_size) / (1.0 * cache_size)
        filter = (freqs >= min_freq) & (freqs <= max_freq)

        #CSV data metrics
        heart_rate = []
        respiration_rate = []
        emotions = []
        
        #Frame data
        bpm = 0
        brpm = 0
        dominant_emotion = 'null'

        #Check if camera is accessible
        if not cap.isOpened():
            print("Camera inaccessible...")
        
        #Check stopping thread condition
        while not self.stop_event.is_set():
            #Capture each frame
            check, frame = cap.read()
            #Set check to true if frame is read correctly
            if not check:
                print("Missing frames, ending capture...")
                break
            
            #Operations on the frame
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) #Set frame colour to grey
            duality = cv.convertScaleAbs(frame, alpha=1.7, beta=0)

            #Face detection parameters
            face = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(face) > 0:
                #Left, top, right, bottom
                (x, y, w, h) = face[0] #Extract face coordinates

                #Emotion recognition using Deepface
                cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                if index % framerate ==  0:
                    try:
                        emotion = DeepFace.analyze(duality, actions=['emotion'], silent=True) #Emotional analysis
                        dominant_emotion = emotion[0]['dominant_emotion']
                        emotions.append(dominant_emotion) #Add emotion to list
                    except Exception as e:
                        print(e) #Display error

                #Heart rate and breathing
                #Fixed size box around face
                x_center = x + w // 2
                y_center = y + h // 2
                half_face_box = face_box // 2
                x1 = max(x_center - half_face_box, 0)
                y1 = max(y_center - half_face_box, 0)
                x2 = min(x_center + half_face_box, frame.shape[1])
                y2 = min(y_center + half_face_box, frame.shape[0])
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
                if len(pyramid[scale]) == len(ROI_gauss[index]):
                    ROI_gauss[index] = pyramid[scale]

                #Apply sast Fourier tranform function to downscaled gauss frame 
                fourier = np.fft.fft(ROI_gauss, axis=0) #From vertical dimension (columns)

                #Apply bandpass filter 
                fourier[filter == False] = 0 #Keep specific frequencies

                #Grab heart and respiration rates 
                if index % heart_calc_freq == 0: #Sampling rate
                    for _ in range(cache_size): #Iterate through cache_size
                        fourier_average[_] = np.real(fourier[_]).mean() #Store signal averages
                    heart_cache[heart_index] = 60.0 * freqs[np.argmax(fourier_average)] #Multiply max values (hertz) by 60 (seconds)
                    bpm = heart_cache.mean() #Average of bpms in heart values cache 
                    brpm = bpm//4 #Calculate breathing

                    heart_rate.append(bpm) #Add bpm to list
                    respiration_rate.append(brpm) #Add brpm to list
                    
                    heart_index = (heart_index + 1) % heart_cahce_size #Increment iterating index

                index = (index + 1) % cache_size #Increment iterating index
                
                #Apply gaussian pyramid function to ROI (scaled up by 3 levels)
                up_ROI = down_ROI #Temporary holder
                pyramid = [up_ROI]
                for _ in range(scale):
                    up = cv.pyrUp(up_ROI) #Upscale frame
                    up_ROI = up #Assign upscaled frame
                    pyramid.append(up_ROI) #Add to list

                #Show ROI in window
                if len(frame[y1:y2, x1:x2]) == len(pyramid[scale]):
                    frame[y1:y2, x1:x2] = pyramid[scale] * 17
                    
            cv.putText(frame, f'BPM: {bpm}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) #Display bpm
            cv.putText(frame, f'BRPM: {brpm}', (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) #Display brpm
            cv.putText(frame, f'Emotion: {dominant_emotion}', (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1) #Display emotion

            #Show frames in a window
            if frame is not None:
                cv.imshow('Janus', frame)
                cv.waitKey(1)
        
        #Zip data making it iterable
        data = zip(heart_rate, respiration_rate, emotions)
        #Save data to CSV file
        self.save_data(data)
                
        #Release capture on closing
        cap.release()
        cv.destroyAllWindows() #Close all windows
        print("Terminating...")