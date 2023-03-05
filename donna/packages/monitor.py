import numpy as np
import csv
import cv2 as cv
from deepface import DeepFace
from tkinter import *

class monitor:
    def cardMonitor():
        print('Monitoring...')

        global stopThread, monitoring, elapsedTime, filepath

        #load Haar face and eye cascades (face shapes)
        faceCascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

        #initiate video capture
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, 640) #set camera resolution - width
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480) #set camera resolution - height
        frameRate = cap.get(cv.CAP_PROP_FPS)  #frames per second

        #face parameters
        faceBox = 200
        dominantEmotion = ''

        #frame parameters
        cvFont = cv.FONT_HERSHEY_SIMPLEX #default font

        #fourier jazz
        minFrequency = 1.0
        maxFrequency = 1.8
        buffer = 100
        index = 0
        fourierAvg = np.zeros((buffer))

        #initialise gaussian pyramid
        ROIGauss = np.zeros((buffer, faceBox//8, faceBox//8, 3))

        #bandpass filter for specific frequencies
        frequencies = (1.0*frameRate) * np.arange(buffer) / (1.0*buffer)
        filter = (frequencies >= minFrequency) & (frequencies <= maxFrequency)

        #heart rate variables
        bpmCalculationFrequency = 30
        bpmindex = 0
        bpmbuffer = 30
        bpmBuffer = np.zeros((bpmbuffer))

        #csv data metrics
        heartRate = []
        respirationRate = []
        emotions = []

        #check if camera is accessible
        if cap.isOpened():
            monitoring = True
        else:
            print("Camera inaccessible...")
            
        while True:
            #capture each frame
            check, frame = cap.read()
            #set ret to true if frame is read correctly
            if not check:
                print("Missing frames, ending capture...")
                break
            
            #operations on the frame
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) #set frame colour to grey
            duality = cv.convertScaleAbs(frame, alpha=1.7, beta=0)

            #face detection parameters
            face = faceCascade.detectMultiScale(gray, 1.3, 5)

            if len(face) > 0:
                #left, top, right, bottom
                (x, y, w, h) = face[0] #extract face coordinates

                #Emotion recognition using Deepface
                cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                if index % frameRate ==  0:
                    try:
                        emotion = DeepFace.analyze(duality, actions=['emotion'], silent=True) #emotional analysis using
                        dominantEmotion = emotion[0]['dominant_emotion']
                        emotions.append(dominantEmotion) #add emotion to list
                        print(emotion[0]['dominant_emotion']) #display main emotion
                    except:
                        print('No face detected.') #display error

                #Heart rate and breathing
                #fixed size box around face
                xCenter = x + w // 2
                yCenter = y + h // 2
                halfFaceBox = faceBox // 2
                x1 = max(xCenter - halfFaceBox, 0)
                y1 = max(yCenter - halfFaceBox, 0)
                x2 = min(xCenter + halfFaceBox, frame.shape[1])
                y2 = min(yCenter + halfFaceBox, frame.shape[0])
                cv.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

                #extract roi from frame
                faceROI = frame[y1:y2, x1:x2]
                levels = faceROI.shape[2]

                #apply gaussian pyramid function to ROI (scaled down image 3 levels)
                downROI = faceROI  #temporary holder
                pyramid = [downROI]
                for _ in range(levels):
                    down = cv.pyrDown(downROI) #downscale frame 
                    downROI = down  #assign downscaled frame
                    pyramid.append(downROI)  #add to list

                #add downscaled gauss frame to index in list
                if len(pyramid[levels]) == len(ROIGauss[index]):
                    ROIGauss[index] = pyramid[levels]

                #apply fast fourier tranform to downscaled gauss frame 
                fourier = np.fft.fft(ROIGauss, axis=0)

                #apply bandpass filter 
                fourier[filter == False] = 0 #keep specific frequencies

                #grab heart and respiration rates 
                if index % bpmCalculationFrequency == 0: #sampling rate
                    for _ in range(buffer): #iterate through buffer
                        fourierAvg[_] = np.real(fourier[_]).mean() #store real signal averages
                    bpmTemp = 60.0 * frequencies[np.argmax(fourierAvg)] #multiply max values (hertz) by 60 (seconds)
                    bpmBuffer[bpmindex] = bpmTemp #add estimate to buffer
                    bpmindex = (bpmindex + 1) % bpmbuffer #increment iterating index
                    bpm = bpmBuffer.mean() #average of bpms in buffer 
                    brpm = bpmBuffer.mean()//4 #calculate breathing

                    heartRate.append(bpm) #add bpm to list
                    respirationRate.append(brpm) #add brpm to list

                    print('BPM: %d' % bpm) #print heart rate
                    print(f'BRPM: {brpm}') #print respiration rate

                index = (index + 1) % buffer #increment iterating index
                
                #apply gaussian pyramid function to ROI (scaled up by 3 levels)
                upROI = downROI #temporary holder
                pyramid = [upROI]
                for _ in range(levels):
                    up = cv.pyrUp(upROI) #upscale frame
                    upROI = up  #assign upscaled frame
                    pyramid.append(upROI)  #add to list

                #show roi in window
                if len(frame[y1:y2, x1:x2]) == len(pyramid[levels]):
                    frame[y1:y2, x1:x2] = pyramid[levels] * 17

            cv.putText(frame, f'BPM: {bpmBuffer.mean()}', (10, 30), cvFont, 0.6, (255, 255, 255), 1) #display bpm
            cv.putText(frame, f'BRPM: {bpmBuffer.mean()//4}', (10, 60), cvFont, 0.6, (255, 255, 255), 1) #display brpm
            cv.putText(frame, f'Emotion: {str(dominantEmotion)}', (10, 90), cvFont, 0.6, (255, 255, 255), 1) #display emotion in frame

            #show frames in a window
            if frame is not None:
                cv.imshow('Janus', frame)
                cv.waitKey(1)

            #termination check
            if stopThread:
                break

        #open the csv file in append mode
        with open(filepath, mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            #write the metrics to the CSV file
            for metric in zip(heartRate, respirationRate, emotions):
                writer.writerow(metric) #write data to file
            print(f'Data written to {filepath}.')
                
        #release capture on closing
        cap.release()
        cv.destroyAllWindows() #close all windows
        print("Terminating...")