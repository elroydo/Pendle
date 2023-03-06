import os
import sys
import time
import datetime
import threading
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
        faceCascade = cv.CascadeClassifier('./assets/classifiers/haarcascade_frontalface_default.xml')

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

#File and folder jazz (does nothing for now)
#path to required resources
def resourcePath(relativePath):
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)

#check if a directory exists
def filePath(relativePath):
    try:
        #check whether the specified path exists or not
        isExist = os.path.exists(relativePath)
        if not isExist:
        #create a new directory if it does not exist
            os.makedirs(relativePath)
            print("The new directory is created.")
    except:
        print("Directory error.")

#Canvas jazz
#point moves left to right repeatedly
def movePoint():
    global functionID, direction, startTime, elapsedTime #access global variables
    elapsedTime = int(time.time() - startTime) #timer
    if direction == 1:
        canvas2.move(point, -12, 0) #move point 10 pixels to the left
        if canvas2.coords(point)[0] < 30: #check coordinates
            direction = 0 #set direction
    else:
        canvas2.move(point, 12, 0) #move point 10 pixels to the right
        if canvas2.coords(point)[2] > 770: #check coordinates
            direction = 1

    if elapsedTime > 0 and elapsedTime % 30 == 0: #show message every 30 seconds
        canvas2.create_text(400, 300, text="Please take a deep breath", font=fontHeading, fill="black", tags="guideText") #create text
    if elapsedTime % 40 >= 33: #delete message after 3 seconds
        canvas2.delete("guideText") #removes old text
    
    if elapsedTime == 300: #5 minute timer
        root.after_cancel(functionID) #stop function
        showCanvas3() #display next screen
    else:
        functionID = canvas2.after(10, movePoint) #update canvas every 10ms

#show and update time
def updateTime():
    canvas1.delete("time") #removes old text
    currentTime = time.strftime("%H:%M:%S") #format string
    canvas1.create_text(400, 20, text=currentTime, font=fontNormal, fill="black", tags="time") #create text
    root.after(1000, updateTime) #recursively update element every second
    
#change between canvases within the window
def showCanvas1(event=None):
    updateTime() #call time function
    helpCanvas.pack_forget() #hide element
    canvas1.pack(fill= BOTH, expand= True) #show element
    canvas1.create_text(400, 400, text="Press here to begin", font=fontHeading, fill="black")
    helpButton.pack()
    helpButton.place(x=750, y=750) #button position on canvas
    
def showCanvas2(event=None):
    global startTime, monitoring
    if monitoring: #check if monitor is up and running
        startTime = time.time() #get current time
    t1.start() #start thread
    canvas1.pack_forget()
    helpButton.pack_forget()
    canvas2.pack()
    movePoint() #call function to move point
    
def showCanvas3(event=None):
    global stopThread
    root.after_cancel(functionID) #stop function
    stopThread = True #terminate thread
    canvas2.pack_forget()
    canvas3.pack()
    canvas3.create_text(400, 400, text="Did you notice anything?", font=fontHeading, fill="black")
    canvas3.create_text(400, 700, text="Press here to continue", font=fontHeading, fill="black")

def showCanvas4(event=None):
    canvas3.pack_forget()
    canvas4.pack()
    canvas4.create_text(400, 400, text="Press here to close", font=fontHeading, fill="black")
    
def showHelpCanvas(event=None):
    canvas1.pack_forget()
    helpButton.pack_forget()
    helpCanvas.create_text(400, 50, text="Pendle Support", font=fontHeading, fill="black")
    #main topic
    helpCanvas.create_rectangle(50, 70, 750, 350, fill="#f5f5f7", outline="#f5f5f7")
    helpCanvas.create_text(400, 100, text="Horizontal eye movements", font=fontSubHeading, fill="black")
    helpCanvas.create_text(400, 200, text="Also known as horizontal saccadic eye movements, will help you remain calm and relaxed.", 
                           font=fontSubHeading2, fill="black", justify="center", width=600)
    #topic two
    helpCanvas.create_rectangle(50, 370, 390, 770, fill="#f5f5f7", outline="#f5f5f7")
    helpCanvas.create_text(220, 400, text="Monitoring", font=fontSubHeading, fill="black")
    helpCanvas.create_text(220, 500, text="Once the session begins, the application will automatically start measuring and recording your heart rate, breathing, and emotions.", 
                           font=fontSubHeading2, fill="black", justify="center", width=300)
    #topic three
    helpCanvas.create_rectangle(410, 370, 750, 770, fill="#f5f5f7", outline="#f5f5f7")
    helpCanvas.create_text(580, 400, text="Feedback", font=fontSubHeading, fill="black")
    helpCanvas.create_text(580, 500, text="From time to time you will see instructions on the screen to follow such as taking a deep breath.", 
                           font=fontSubHeading2, fill="black", justify="center", width=300)
    helpCanvas.pack()
    
#create frame instance
root = Tk()
root.title("Pendle")
root.geometry('800x800') #set geometry
root.resizable(False, False)

#create canvas windows
height = 800
width = 800
canvas1 = Canvas(root, width=width, height=height)
canvas2 = Canvas(root, width=width, height=height)
canvas3 = Canvas(root, width=width, height=height)
canvas4 = Canvas(root, width=width, height=height)
helpCanvas = Canvas(root, width=width, height=height)

#create canvas buttons
canvas1.bind("<Button-1>", showCanvas2) #begin
canvas2.bind("<Button-1>", showCanvas3) #go to end
canvas3.bind("<Button-1>", showCanvas4) #go to end
canvas4.bind("<Button-1>", lambda event: root.quit()) #close window
helpCanvas.bind("<Button-1>", showCanvas1) #go to start

#help button
helpIcon = PhotoImage(file='./assets/icons/question.png')
helpButton = Button(canvas1, text="Help", command=showHelpCanvas, image=helpIcon, relief=FLAT) #create button

#create a point
x = width//2 #calculate x centre
y = height//2 #calculate y centre
radius = 10 #set point radius
point = canvas2.create_oval(x - radius, y - radius, x + radius, y + radius, fill="black")
direction = 0 #add direction

#create font styles
fontHeading = ("Arial", 20, "bold")
fontSubHeading = ("Arial", 18, "bold")
fontSubHeading2 = ("Arial", 16)
fontNormal = ("Arial", 10)

#cycles
functionID = 0 #initialise variable
startTime = time.time() #initialise time
elapsedTime = int(time.time() - startTime)

#csv jazz
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"data_{timestamp}.csv"
folder = 'data/'
filepath = os.path.join(folder, filename) #get the full path

if not os.path.isfile(filepath): #check if file exists
    headers = ('bpm', 'bpm', 'emotions') #initialise headers
    with open(filepath, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['bpm', 'brpm', 'emotions'])
    print(f'{filepath} created.')
else:
    print(f'{filepath} already exists.')

#threading jazz
t1 = threading.Thread(target=monitor.cardMonitor, daemon=True)
monitoring = False #initialise flag
stopThread = False #initialise flag

showCanvas1() #show main screen

root.mainloop() #run gui