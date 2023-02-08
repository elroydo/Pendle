from tkinter import *

#point moves left to right repeatedly
def move_point():
    global direction #access global variable
    if direction == 'right':
        canvas_2.move(point, -10, 0) #move point 10 pixels to the left
        if canvas_2.coords(point)[0] < 10:  #check coordinates
            direction = 'left' #set direction
    else:
        canvas_2.move(point, 10, 0) #move point 10 pixels to the right
        if canvas_2.coords(point)[2] > 790: #check coordinates
            direction = 'right'
    canvas_2.after(10, move_point) #update canvals every 10ms
    
#change between canvases within the window
def show_canvas_1(event=None):
    help_canvas.pack_forget() #hide element
    canvas_1.pack(fill= BOTH, expand= True) #show element
    help_button.pack()
    help_button.place(x=750, y=750)
    
def show_canvas_2(event=None):
    canvas_1.pack_forget()
    help_button.pack_forget()
    canvas_2.pack()
    
def show_canvas_3(event=None):
    canvas_2.pack_forget()
    canvas_3.pack()
    
def show_help_canvas(event=None):
    canvas_1.pack_forget()
    help_button.pack_forget()
    help_canvas.pack()

#create frame instance
root = Tk()
root.title("Belladonna")
root.geometry('800x800') #set geometry
root.resizable(False, False)

#create canvas windows
canvas_1 = Canvas(root, width=800, height=800, bg="#D1FFE5")
canvas_2 = Canvas(root, width=800, height=800, bg="#DEFFFF")
canvas_3 = Canvas(root, width=800, height=800, bg="#FFC9C4")
help_canvas = Canvas(root, width=800, height=800, bg="#D1E7FF")

#create canvas buttons
canvas_1.bind("<Button-1>", show_canvas_2) #make canvas button
canvas_2.bind("<Button-1>", show_canvas_3)
canvas_3.bind("<Button-1>", lambda event: root.quit()) #close window
help_canvas.bind("<Button-1>", show_canvas_1)

#help button
help_button = Button(canvas_1, text="Help", command=show_help_canvas, relief=FLAT, bg="#D1FFE5")
help_icon = PhotoImage(file='assets/icons/question.png')
help_button.config(image=help_icon)

#create a point
point = canvas_2.create_oval(380, 380, 400, 400, fill="black")
direction = 'left' #add direction

show_canvas_1() #show main screen
move_point() #move point

root.mainloop()