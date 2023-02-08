import time
from tkinter import *
import threading

#separate task using threads; for tracking heart rate, emotions, and breathing
def background_task():
    while True:
        print("background task running...")
        time.sleep(1) #half for a second

#point moves left to right repeatedly
def move_point():
    global direction #access global variable
    if direction == 'right':
        canvas_2.move(point, -10, 0) #move point 10 pixels to the left
        if canvas_2.coords(point)[0] < 30:  #check coordinates
            direction = 'left' #set direction
    else:
        canvas_2.move(point, 10, 0) #move point 10 pixels to the right
        if canvas_2.coords(point)[2] > 770: #check coordinates
            direction = 'right'
    canvas_2.after(10, move_point) #update canvals every 10ms
    
#show and update time
def update_time():
    canvas_1.delete("time") #removes old text
    current_time = time.strftime("%H:%M:%S") #format string
    canvas_1.create_text(400, 20, text=current_time, font=font_normal, fill="black", tags="time") #create text
    root.after(1000, update_time) #recursively update element every second
    
#change between canvases within the window
def show_canvas_1(event=None):
    update_time() #call time function
    help_canvas.pack_forget() #hide element
    canvas_1.pack(fill= BOTH, expand= True) #show element
    canvas_1.create_text(400, 400, text="Press here to begin", font=font_heading, fill="black")
    help_button.pack()
    help_button.place(x=750, y=750) #button position on canvas
    
def show_canvas_2(event=None):
    canvas_1.pack_forget()
    help_button.pack_forget()
    canvas_2.pack()
    
def show_canvas_3(event=None):
    canvas_2.pack_forget()
    canvas_3.pack()
    canvas_3.create_text(400, 400, text="Press here to close", font=font_heading, fill="black")
    
def show_help_canvas(event=None):
    canvas_1.pack_forget()
    help_button.pack_forget()
    help_canvas.create_text(400, 50, text="Pendle Support", font=font_heading, fill="black")
    help_canvas.pack()
    

#create frame instance
root = Tk()
root.title("Pendle")
root.geometry('800x800') #set geometry
root.resizable(False, False)

#create font styles
font_heading = ("Arial", 20, "bold")
font_normal = ("Arial", 10)

#create canvas windows
canvas_1 = Canvas(root, width=800, height=800)
canvas_2 = Canvas(root, width=800, height=800)
canvas_3 = Canvas(root, width=800, height=800)
help_canvas = Canvas(root, width=800, height=800)

#create canvas buttons
canvas_1.bind("<Button-1>", show_canvas_2) #make canvas button
canvas_2.bind("<Button-1>", show_canvas_3)
canvas_3.bind("<Button-1>", lambda event: root.quit()) #close window
help_canvas.bind("<Button-1>", show_canvas_1)

#help button
help_button = Button(canvas_1, text="Help", command=show_help_canvas, relief=FLAT)
help_icon = PhotoImage(file='assets/icons/question.png')
help_button.config(image=help_icon)

#create a point
point = canvas_2.create_oval(380, 380, 400, 400, fill="black")
direction = 'left' #add direction

show_canvas_1() #show main screen
move_point() #move point

#threading jazz
#inline
#t = threading.Thread(target=background_task, daemon=True).start()
thread = threading.Thread(target=background_task)
thread.daemon = True #daemon thread to main thread
thread.start() #start thread

root.mainloop()