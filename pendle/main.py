import sys
import time
from tkinter import BOTH, FLAT, Button, Canvas, PhotoImage, TclError, Tk, messagebox

# Import package
from packages.physiology import Physiology

class PendleApp:
    def __init__(self):
        # Create fixed size frame instance
        self.pendle = Tk()
        # Initialize class attributes and create canvases, buttons, and other GUI elements
        self.pendle.title("Pendle")
        self.pendle.geometry('800x800')
        self.pendle.resizable(False, False)
        self.pendle.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create canvas windows
        height = 800
        width = 800
        self.start_screen = Canvas(self.pendle, width=width, height=height) # Start
        self.waiting_screen = Canvas(self.pendle, width=width, height=height) # Pre-session
        self.session_screen = Canvas(self.pendle, width=width, height=height) # Session
        self.post_session_screen = Canvas(self.pendle, width=width, height=height) # Post-session
        self.end_screen = Canvas(self.pendle, width=width, height=height) # End
        self.help_screen = Canvas(self.pendle, width=width, height=height) # Help

        # Create font styles
        self.font_heading = ("Arial", 28, "bold")
        self.font_sub_heading = ("Arial", 16, "bold")
        self.font_sub_heading2 = ("Arial", 14)
        self.font_normal = ("Arial", 10)

        # Import icons
        self.help_icon = PhotoImage(file='./assets/images/question.png')
        self.restart_icon = PhotoImage(file='./assets/images/restart.png')

        # Create buttons and bindings
        self.start_screen.bind("<Button-1>", self.show_waiting_screen) # To Waiting screen
        self.session_screen.bind("<Button-1>", self.confirm_end_session) # To Post-session screen
        self.post_session_screen.bind("<Button-1>", self.show_end_screen) # To End screen
        self.help_screen.bind("<Button-1>", lambda event: self.toggle_canvas(self.start_screen, self.help_screen)) # To Start screen
        self.end_screen.bind("<Button-1>", lambda event: self.pendle.quit()) # Quit application

        helpButton = Button(self.start_screen, text="Help", command=self.show_help_screen, image=self.help_icon, relief=FLAT)
        restartButton = Button(self.end_screen, text="Restart", command=self.show_start_screen, image=self.restart_icon, relief=FLAT)

        helpButton.pack()
        helpButton.place(x=750, y=750) # Position on canvas
        restartButton.pack(fill=BOTH, expand=True)
        restartButton.place(x=750, y=750)

        # Create shapes
        x = width//2 # Calculate x centre
        y = height//2 # Calculate y centre
        radius = 10
        self.ball = self.session_screen.create_oval(x - radius, y - radius, x + radius, y + radius, fill="black")

        self.help_screen.create_rectangle(50, 100, 750, 350, fill="#f5f5f7", outline="#f5f5f7")
        self.help_screen.create_rectangle(50, 370, 390, 700, fill="#f5f5f7", outline="#f5f5f7")
        self.help_screen.create_rectangle(410, 370, 750, 700, fill="#f5f5f7", outline="#f5f5f7")

        # Create text elements
        self.start_screen.create_text(400, 400, text="Tap here to start", font=self.font_heading, fill="black")
        self.start_screen.create_text(400, 750, text="Please get comfortable and ensure your camera can clearly see you", font=self.font_sub_heading2, fill="black")

        self.waiting_screen.create_text(400, 400, text="Please stay focused and follow the moving object and instructions on your screen", font=self.font_heading, fill="black", justify="center", width=700)
        self.waiting_screen.create_text(400, 750, text="End your 5-minute session at any time by tapping anywhere on the screen", font=self.font_sub_heading2, fill="black")

        self.help_screen.create_text(400, 50, text="Pendle Support", font=self.font_heading, fill="black")
        self.help_screen.create_text(400, 130, text="Your 5-Minute relaxation session", font=self.font_sub_heading, fill="black")
        self.help_screen.create_text(400, 230, text="Pendle uses a swinging ball, inspired by Eye-Movement Desensitisation and Reprocessing (EMDR) therapy, to help you process your experiences while feeling calm and relaxed.", font=self.font_sub_heading2, fill="black", justify="center", width=600)
        self.help_screen.create_text(220, 400, text="Monitoring your body", font=self.font_sub_heading, fill="black")
        self.help_screen.create_text(220, 530, text="During the session, Pendle will monitor and record your heart rate, breathing, and emotions.", font=self.font_sub_heading2, fill="black", justify="center", width=300)
        self.help_screen.create_text(580, 400, text="Giving you feedback", font=self.font_sub_heading, fill="black")
        self.help_screen.create_text(580, 530, text="Occasionally, you will see on-screen instructions to follow, like taking a deep breath.", font=self.font_sub_heading2, fill="black", justify="center", width=300)
        self.help_screen.create_text(400, 750, text="Tap here to go back", font=self.font_sub_heading, fill="black")
        self.help_screen.create_text(400, 785, text="Question & Reload  icons created by Freepik - Flaticon", font=self.font_normal, fill="#dddddd")

        self.post_session_screen.create_text(400, 400, text="Did you happen to notice anything?", font=self.font_heading, fill="black")
        self.post_session_screen.create_text(400, 750, text="Tap here to proceed", font=self.font_sub_heading, fill="black")

        self.end_screen.create_text(400, 400, text="Tap here to close", font=self.font_heading, fill="black")

        # Session parameters
        self.function_ID = 0
        self.start_time = time.time()
        self.elapsed_time = int(time.time() - self.start_time)
        self.direction = 0

    # Alternating ball
    def move_ball(self):
        # Timer
        self.elapsed_time = int(time.time() - self.start_time)
        self.move_distance = 12
        self.left_limit, self.right_limit = 30, 770
        # Move ball from left to right
        if self.direction == 1:
            self.session_screen.move(self.ball, -self.move_distance, 0)
            if self.session_screen.coords(self.ball)[0] < self.left_limit:
                self.direction = 0
        else:
            self.session_screen.move(self.ball, self.move_distance, 0)
            if self.session_screen.coords(self.ball)[2] > self.right_limit:
                self.direction = 1
        # Show message every 30 seconds and delete after 3 seconds
        if self.elapsed_time > 0 and self.elapsed_time % 30 == 0:
            self.session_screen.create_text(400, 300, text="Please take a deep breath", font=self.font_heading, fill="black", tags="feedback")
        elif self.elapsed_time % 40 >= 33:
            self.session_screen.delete("feedback")
        # 5 minute timer
        if self.elapsed_time >= 300:
            self.pendle.after_cancel(self.function_ID)
            self.show_post_screen()
        else:
            # Update canvas every 10ms
            self.function_ID = self.session_screen.after(10, self.move_ball)
            
    # Toggle canvases
    def toggle_canvas(self, show_canvas, *hide_canvases):
        for self.canvas in hide_canvases:
            self.canvas.pack_forget()
        show_canvas.pack(fill=BOTH, expand=True)

    # Display pre-session timer
    def countdown_timer(self, time_left):
        if time_left > 0:
            self.waiting_screen.delete("time")
            self.waiting_screen.create_text(400, 50, text=f"Session starts in...{str(time_left)}", font=self.font_sub_heading2, fill="black", tags="time")
            self.pendle.after(1000, self.countdown_timer, time_left-1)

    # Confirmation dialogue
    def confirm_end_session(self, event=None):
        result = messagebox.askyesno("Please confirm", "Are you certain you wish to end your session?")
        if result == True:
            self.show_post_screen()
        else:
            pass

    # Exit application
    def on_closing(self):
        try:
            self.pendle.destroy()
        except TclError:
            sys.exit()

    # Screen canvases
    def show_start_screen(self, event=None):
        global monitor
        # Create and start thread instance
        monitor = Physiology() 
        monitor.start()
        self.toggle_canvas(self.start_screen, self.help_screen, self.end_screen)

    def show_waiting_screen(self, event=None):
        self.countdown_timer(10)
        self.toggle_canvas(self.waiting_screen, self.start_screen)
        self.pendle.after(10000, self.show_session_screen) # Wait 10 seconds

    def show_session_screen(self, event=None):
        # Set start time and session in progress
        self.start_time = time.time()
        monitor.toggle_session()
        self.move_ball()
        self.toggle_canvas(self.session_screen, self.waiting_screen)

    def show_post_screen(self, event=None):
        # Set Session inactive and stop function
        monitor.toggle_session()
        self.pendle.after_cancel(self.function_ID)
        self.toggle_canvas(self.post_session_screen, self.session_screen)

    def show_end_screen(self, event=None):
        # Stop thread allowing it to completely terminate
        monitor.stop()
        monitor.join()
        self.toggle_canvas(self.end_screen, self.post_session_screen)

    def show_help_screen(self, event=None):
        self.toggle_canvas(self.help_screen, self.start_screen)

    # Run GUI
    def start(self):
        self.show_start_screen()
        self.pendle.mainloop()

# At the end of the file
if __name__ == "__main__":
    app = PendleApp()
    app.start()