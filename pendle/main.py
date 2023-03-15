#Import libraries
import sys
import time
from tkinter import BOTH, FLAT, Button, Canvas, PhotoImage, TclError, Tk, messagebox

#Import package
from packages.physiology import Physiology

#GUI jazz
##Point moves left to right repeatedly
def move_point():
    global function_ID, start_time, direction #Access global variables

    elapsed_time = int(time.time() - start_time) #Timer
    if direction == 1:
        session_screen.move(point, -12, 0) #Move point 10 pixels to the left
        if session_screen.coords(point)[0] < 30: #Check coordinates
            direction = 0 #Left
    else:
        session_screen.move(point, 12, 0) #Move point 10 pixels to the right
        if session_screen.coords(point)[2] > 770:
            direction = 1 #Right

    if elapsed_time > 0 and elapsed_time % 30 == 0: #Show message every 30 seconds
        session_screen.create_text(400, 300, text="Please take a deep breath", font=font_heading, fill="black", tags="feedback") #Create text
    if elapsed_time % 40 >= 33: #Delete message after 3 seconds
        session_screen.delete("feedback") #Removes old text
    
    if elapsed_time >= 300: #5 minute timer
        pendle.after_cancel(function_ID) #Stop function
        show_post_screen() #Display next screen
    else:
        function_ID = session_screen.after(10, move_point) #Update canvas every 10ms
        
def countdown_timer(time_left):
    if time_left > 0:
        waiting_screen.delete("time") #Remove old text
        waiting_screen.create_text(400, 50, text=f"Session starts in...{str(time_left)}", font=font_sub_heading2, fill="black", tags="time") #Display time left
        pendle.after(1000, countdown_timer, time_left-1) #Update countdown after 1 second

#Confirmation dialogue
def confirm_end_session(event=None):
    result = messagebox.askyesno("Please confirm", "Are you certain you wish to end your session?")
    if result == True:
        show_post_screen() #Show Post screen
    else:
        pass #Stay on the same canvas

#Toggle canvases
def toggle_canvas(canvas, prev_canvas=None):
    if prev_canvas:
        prev_canvas.pack_forget()
    if canvas.winfo_viewable():
        canvas.pack_forget()
    else:
        canvas.pack()
        
#Exit application
def on_closing():
    try:
        pendle.destroy()
    except TclError:
        sys.exit()
    
#Change between canvases within the window
def show_start_screen(event=None):
    global monitor
    
    monitor = Physiology() #Create thread instance
    monitor.start() #Start thread
    
    help_screen.pack_forget() #Hide element
    end_screen.pack_forget()
    
    start_screen.create_text(400, 400, text="Tap here to start", font=font_heading, fill="black")
    start_screen.create_text(400, 750, text="Please get comfortable and ensure your camera can clearly see you", font=font_sub_heading2, fill="black")
    helpButton.pack()
    helpButton.place(x=750, y=750) #Button position on canvas
    start_screen.pack(fill=BOTH, expand= True) #Show element
    
def show_waiting_screen(event=None):
    start_screen.pack_forget()
    helpButton.pack_forget()
    countdown_timer(10)
    waiting_screen.create_text(400, 400, text="Please stay focused and follow the moving object and instructions on your screen",font=font_heading, fill="black", justify="center", width=700)
    waiting_screen.create_text(400, 750, text="End your 5-minute session at any time by tapping anywhere on the screen", font=font_sub_heading2, fill="black")
    waiting_screen.pack(fill=BOTH, expand= True)
    pendle.after(10000, show_session_screen) #Wait 10 seconds

def show_session_screen(event=None):
    global start_time

    start_time = time.time() #Set start time
    monitor.toggle_session() #Session in progress

    waiting_screen.pack_forget()
    move_point() #Call function to move point
    session_screen.pack(fill=BOTH, expand= True)

def show_post_screen(event=None):
    monitor.toggle_session() #Session no longer in progress

    pendle.after_cancel(function_ID) #Stop function

    session_screen.pack_forget()
    post_session_screen.create_text(400, 400, text="Did you happen to notice anything?", font=font_heading, fill="black")
    post_session_screen.create_text(400, 750, text="Tap here to proceed", font=font_sub_heading, fill="black")
    post_session_screen.pack(fill=BOTH, expand= True)

def show_end_screen(event=None):
    monitor.stop() #Stop thread
    monitor.join() #Allow thread to completely terminate
    
    post_session_screen.pack_forget()
    end_screen.create_text(400, 400, text="Tap here to close", font=font_heading, fill="black")
    restartButton.pack(fill=BOTH, expand= True)
    restartButton.place(x=750, y=750)
    end_screen.pack()
    
def show_help_screen(event=None):
    start_screen.pack_forget()
    helpButton.pack_forget()
    help_screen.create_text(400, 50, text="Pendle Support", font=font_heading, fill="black")
    #Main topic
    help_screen.create_rectangle(50, 100, 750, 350, fill="#f5f5f7", outline="#f5f5f7")
    help_screen.create_text(400, 130, text="Your 5-Minute relaxation session", font=font_sub_heading, fill="black")
    help_screen.create_text(400, 230, text="Pendle uses a swinging point, inspired by Eye-Movement Desensitisation and Reprocessing (EMDR) therapy, to help you process your experiences while feeling calm and relaxed.", 
                           font=font_sub_heading2, fill="black", justify="center", width=600)
    #Topic two
    help_screen.create_rectangle(50, 370, 390, 700, fill="#f5f5f7", outline="#f5f5f7")
    help_screen.create_text(220, 400, text="Monitoring your body", font=font_sub_heading, fill="black")
    help_screen.create_text(220, 530, text="During the session, Pendle will monitor and record your heart rate, breathing, and emotions.", 
                           font=font_sub_heading2, fill="black", justify="center", width=300)
    #Topic three
    help_screen.create_rectangle(410, 370, 750, 700, fill="#f5f5f7", outline="#f5f5f7")
    help_screen.create_text(580, 400, text="Giving you feedback", font=font_sub_heading, fill="black")
    help_screen.create_text(580, 530, text="Occasionally, you will see on-screen instructions to follow, like taking a deep breath.", 
                           font=font_sub_heading2, fill="black", justify="center", width=300)
    help_screen.create_text(400, 750, text="Tap here to go back", font=font_sub_heading, fill="black")
    help_screen.pack(fill=BOTH, expand= True)
    
#Create frame instance
pendle = Tk()
pendle.title("Pendle")
pendle.geometry('800x800') #Set geometry
pendle.resizable(False, False) #Set fixed window size
pendle.protocol("WM_DELETE_WINDOW", on_closing) #Destroy instance upon closing

#Create canvas windows
screen_height = 800
screen_width = 800
start_screen = Canvas(pendle, width=screen_width, height=screen_height) #Start
waiting_screen = Canvas(pendle, width=screen_width, height=screen_height) #Waiting
session_screen = Canvas(pendle, width=screen_width, height=screen_height) #Session
post_session_screen = Canvas(pendle, width=screen_width, height=screen_height) #Post-session
end_screen = Canvas(pendle, width=screen_width, height=screen_height) #End
help_screen = Canvas(pendle, width=screen_width, height=screen_height) #Help

#Create canvas buttons
start_screen.bind("<Button-1>", show_waiting_screen) #To Waiting screen 
session_screen.bind("<Button-1>", confirm_end_session) #To Post-session screen 
post_session_screen.bind("<Button-1>", show_end_screen) #To End screen 
help_screen.bind("<Button-1>", lambda event: toggle_canvas(start_screen, help_screen)) #To Start screen 
end_screen.bind("<Button-1>", lambda event: pendle.quit()) #Quit application 

#Buttons
help_icon = PhotoImage(file='./assets/images/question.png') #Import help icon
restart_icon = PhotoImage(file='./assets/images/restart.png') #Import restart icon
helpButton = Button(start_screen, text="Help", command=show_help_screen, image=help_icon, relief=FLAT) #Create help button
restartButton = Button(end_screen, text="Restart", command=show_start_screen, image=restart_icon, relief=FLAT) #Create restart button

#Create a point
x = screen_width//2 #Calculate x centre
y = screen_height//2 #Calculate y centre
radius = 10 #Set radius
point = session_screen.create_oval(x - radius, y - radius, x + radius, y + radius, fill="black") #Create point
direction = 0 #Add direction

#Create font styles
font_heading = ("Arial", 28, "bold")
font_sub_heading = ("Arial", 16, "bold")
font_sub_heading2 = ("Arial", 14)
font_normal = ("Arial", 10)

#Cycles
function_ID = 0 #Initialise variable
start_time = time.time() #Initialise time
elapsed_time = int(time.time() - start_time)  #Initialise elapsed time

#Threading jazz
monitor = Physiology()

#Show start screen
show_start_screen() #Show main screen

#Run GUI
pendle.mainloop()