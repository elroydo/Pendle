import time
import threading
import numpy as np
import cv2 as cv
from deepface import DeepFace
from tkinter import *

def cardMonitor():
    print('Monitoring...')

    global stopThread, elapsedTime

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
    font = cv.FONT_HERSHEY_SIMPLEX #default font

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

    #check if camera is accessible
    if not cap.isOpened():
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
        duality = cv.convertScaleAbs(frame, alpha=1.5, beta=0)

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
                bpm = 60.0 * frequencies[np.argmax(fourierAvg)] #multiply max values (hertz) by 60 (seconds)
                bpmBuffer[bpmindex] = bpm #add estimate to buffer
                bpmindex = (bpmindex + 1) % bpmbuffer #increment iterating index
                print('BPM: %d' % bpmBuffer.mean())  #print heart rate
                print(f'BRPM: {bpmBuffer.mean()//4}') #calculate and print respiration rate

            index = (index + 1) % buffer #increment iterating index
            
            #apply gaussian pyramid function to ROI (scaled up by 3 levels)
            upROI = downROI #temporary holder
            pyramid = [upROI]
            for _ in range(levels):
                up = cv.pyrUp(upROI) #upscale frame
                upROI = up  #assign upscaled frame
                pyramid.append(upROI)  #add to list
            
            if len(frame[y1:y2, x1:x2]) == len(pyramid[levels]):
                frame[y1:y2, x1:x2] = pyramid[levels] * 17

        cv.putText(frame, f'BPM: {bpmBuffer.mean()}', (10, 30), font, 0.6, (255, 255, 255), 1) #display bpm
        cv.putText(frame, f'BRPM: {bpmBuffer.mean()//4}', (10, 60), font, 0.6, (255, 255, 255), 1) #display brpm
        cv.putText(frame, f'Emotion: {str(dominantEmotion)}', (10, 90), font, 0.6, (255, 255, 255), 1) #display emotion in frame

        #show frames in a window
        if frame is not None:
            cv.imshow('Janus', frame)
            cv.waitKey(1)

        #termination check
        if stopThread:
            break
            
    #release capture on closing
    cap.release()
    cv.destroyAllWindows() #close all windows
    print("Terminating...")

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
    global startTime
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
    canvas3.create_oval(380, 380, 400, 400, fill="black") #create static point in the centre
    canvas3.create_text(400, 300, text="Focus on the point below and take a deep breath.", font=fontHeading, fill="black")

def showCanvas4(event=None):
    canvas3.pack_forget()
    canvas4.pack()
    canvas4.create_text(400, 400, text="Press here to close", font=fontHeading, fill="black")
    
def showHelpCanvas(event=None):
    canvas1.pack_forget()
    helpButton.pack_forget()
    helpCanvas.create_text(400, 50, text="Pendle Support", font=fontHeading, fill="black")
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
helpButton = Button(canvas1, text="Help", command=showHelpCanvas, relief=FLAT) #create button
helpButton.config(image=PhotoImage(file='assets/icons/question.png')) #import icon

#create a point
x = width//2 #calculate x centre
y = height//2 #calculate y centre
radius = 10 #set point radius
point = canvas2.create_oval(x - radius, y - radius, x + radius, y + radius, fill="black")
direction = 0 #add direction

#create font styles
fontHeading = ("Arial", 20, "bold")
fontNormal = ("Arial", 10)

#cycles
functionID = 0 #initialise variable
startTime = time.time() #initialise time
elapsedTime = int(time.time() - startTime)

#threading jazz
t1 = threading.Thread(target=cardMonitor, daemon=True)
stopThread = False #initialise flag

showCanvas1() #show main screen

root.mainloop() #run gui