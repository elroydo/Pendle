import sys
import time
from tkinter import BOTH, FLAT, Button, Canvas, PhotoImage, TclError, Tk, messagebox

# Import package
from packages.physiology import Physiology

# Ball alternates laterally
def move_ball():
    global function_ID, start_time, direction
    # Timer
    elapsed_time = int(time.time() - start_time)
    move_distance = 12
    left_limit, right_limit = 30, 770
    # Move ball from left to right
    if direction == 1:
        session_screen.move(ball, -move_distance, 0)
        if session_screen.coords(ball)[0] < left_limit:
            direction = 0
    else:
        session_screen.move(ball, move_distance, 0)
        if session_screen.coords(ball)[2] > right_limit:
            direction = 1
    # Show message every 30 seconds and delete after 3 seconds
    if elapsed_time > 0 and elapsed_time % 30 == 0:
        session_screen.create_text(400, 300, text="Please take a deep breath", font=font_heading, fill="black", tags="feedback")
    elif elapsed_time % 40 >= 33:
        session_screen.delete("feedback")
    # 5 minute timer
    if elapsed_time >= 300:
        pendle.after_cancel(function_ID)
        show_post_screen()
    else:
        # Update canvas every 10ms
        function_ID = session_screen.after(10, move_ball)
        
# Toggle canvases
def toggle_canvas(show_canvas, *hide_canvases):
    for canvas in hide_canvases:
        canvas.pack_forget()
    show_canvas.pack(fill=BOTH, expand=True)

# Display pre-session timer
def countdown_timer(time_left):
    if time_left > 0:
        waiting_screen.delete("time")
        waiting_screen.create_text(400, 50, text=f"Session starts in...{str(time_left)}", font=font_sub_heading2, fill="black", tags="time")
        pendle.after(1000, countdown_timer, time_left-1)

# Confirmation dialogue
def confirm_end_session(event=None):
    result = messagebox.askyesno("Please confirm", "Are you certain you wish to end your session?")
    if result == True:
        show_post_screen()
    else:
        pass

# Exit application
def on_closing():
    try:
        pendle.destroy()
    except TclError:
        sys.exit()

# Screen canvases
def show_start_screen(event=None):
    global monitor
    # Create and start thread instance
    monitor = Physiology() 
    monitor.start()
    toggle_canvas(start_screen, help_screen, end_screen)

def show_waiting_screen(event=None):
    countdown_timer(10)
    toggle_canvas(waiting_screen, start_screen)
    pendle.after(10000, show_session_screen) # Wait 10 seconds

def show_session_screen(event=None):
    global start_time
     # Set start time and session in progress
    start_time = time.time()
    monitor.toggle_session()
    move_ball()
    toggle_canvas(session_screen, waiting_screen)

def show_post_screen(event=None):
     # Set Session inactive and stop function
    monitor.toggle_session()
    pendle.after_cancel(function_ID)
    toggle_canvas(post_session_screen, session_screen)

def show_end_screen(event=None):
     # Stop thread allowing it to completely terminate
    monitor.stop()
    monitor.join()
    toggle_canvas(end_screen, post_session_screen)

def show_help_screen(event=None):
    toggle_canvas(help_screen, start_screen)

# Create fixed size frame instance
pendle = Tk()
pendle.title("Pendle")
pendle.geometry('800x800')
pendle.resizable(False, False)
pendle.protocol("WM_DELETE_WINDOW", on_closing)

# Create canvas windows
height = 800
width = 800
start_screen = Canvas(pendle, width=width, height=height) # Start
waiting_screen = Canvas(pendle, width=width, height=height) # Pre-session
session_screen = Canvas(pendle, width=width, height=height) # Session
post_session_screen = Canvas(pendle, width=width, height=height) # Post-session
end_screen = Canvas(pendle, width=width, height=height) # End
help_screen = Canvas(pendle, width=width, height=height) # Help

# Create font styles
font_heading = ("Arial", 28, "bold")
font_sub_heading = ("Arial", 16, "bold")
font_sub_heading2 = ("Arial", 14)
font_normal = ("Arial", 10)

# Import icons
help_icon = PhotoImage(file='./assets/images/question.png')
restart_icon = PhotoImage(file='./assets/images/restart.png')

# Create buttons and bindings
start_screen.bind("<Button-1>", show_waiting_screen) # To Waiting screen
session_screen.bind("<Button-1>", confirm_end_session) # To Post-session screen
post_session_screen.bind("<Button-1>", show_end_screen) # To End screen
help_screen.bind("<Button-1>", lambda event: toggle_canvas(start_screen, help_screen)) # To Start screen
end_screen.bind("<Button-1>", lambda event: pendle.quit()) # Quit application

helpButton = Button(start_screen, text="Help", command=show_help_screen, image=help_icon, relief=FLAT)
restartButton = Button(end_screen, text="Restart", command=show_start_screen, image=restart_icon, relief=FLAT)

helpButton.pack()
helpButton.place(x=750, y=750) # Position on canvas
restartButton.pack(fill=BOTH, expand=True)
restartButton.place(x=750, y=750)

# Create shapes
x = width//2 # Calculate x centre
y = height//2 # Calculate y centre
radius = 10
ball = session_screen.create_oval(x - radius, y - radius, x + radius, y + radius, fill="black")

help_screen.create_rectangle(50, 100, 750, 350, fill="#f5f5f7", outline="#f5f5f7")
help_screen.create_rectangle(50, 370, 390, 700, fill="#f5f5f7", outline="#f5f5f7")
help_screen.create_rectangle(410, 370, 750, 700, fill="#f5f5f7", outline="#f5f5f7")

# Create text elements
start_screen.create_text(400, 400, text="Tap here to start", font=font_heading, fill="black")
start_screen.create_text(400, 750, text="Please get comfortable and ensure your camera can clearly see you", font=font_sub_heading2, fill="black")

waiting_screen.create_text(400, 400, text="Please stay focused and follow the moving object and instructions on your screen", font=font_heading, fill="black", justify="center", width=700)
waiting_screen.create_text(400, 750, text="End your 5-minute session at any time by tapping anywhere on the screen", font=font_sub_heading2, fill="black")

help_screen.create_text(400, 50, text="Pendle Support", font=font_heading, fill="black")
help_screen.create_text(400, 130, text="Your 5-Minute relaxation session", font=font_sub_heading, fill="black")
help_screen.create_text(400, 230, text="Pendle uses a swinging ball, inspired by Eye-Movement Desensitisation and Reprocessing (EMDR) therapy, to help you process your experiences while feeling calm and relaxed.", font=font_sub_heading2, fill="black", justify="center", width=600)
help_screen.create_text(220, 400, text="Monitoring your body", font=font_sub_heading, fill="black")
help_screen.create_text(220, 530, text="During the session, Pendle will monitor and record your heart rate, breathing, and emotions.", font=font_sub_heading2, fill="black", justify="center", width=300)
help_screen.create_text(580, 400, text="Giving you feedback", font=font_sub_heading, fill="black")
help_screen.create_text(580, 530, text="Occasionally, you will see on-screen instructions to follow, like taking a deep breath.", font=font_sub_heading2, fill="black", justify="center", width=300)
help_screen.create_text(400, 750, text="Tap here to go back", font=font_sub_heading, fill="black")
help_screen.create_text(400, 785, text="Question & Reload  icons created by Freepik - Flaticon", font=font_normal, fill="#dddddd")

post_session_screen.create_text(400, 400, text="Did you happen to notice anything?", font=font_heading, fill="black")
post_session_screen.create_text(400, 750, text="Tap here to proceed", font=font_sub_heading, fill="black")

end_screen.create_text(400, 400, text="Tap here to close", font=font_heading, fill="black")

# Session parameters
function_ID = 0
start_time = time.time()
elapsed_time = int(time.time() - start_time)
direction = 0 # Add direction

# Show start screen
show_start_screen()

# Run GUI
pendle.mainloop()