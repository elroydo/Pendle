from tkinter import *

#point moves left to right repeatedly
def move_point():
    global direction #access global variable
    if direction == 'right':
        canvas_2.move(point, -5, 0) #move point 5 pixels to the left
        if canvas_2.coords(point)[0] < 0:  #check coordinates
            direction = 'left' #set direction
    else:
        canvas_2.move(point, 5, 0) #move point 5 pixels to the right
        if canvas_2.coords(point)[2] > 800: #check coordinates
            direction = 'right'
    canvas_2.after(10, move_point) #update canvals every 10ms
    
#change between canvases within the window
def show_canvas_1(event=None):
    canvas_2.pack_forget() #hide element
    button_2.pack_forget()
    button_3.pack_forget()
    button_1.pack() #show element
    canvas_1.pack()  

def show_canvas_2(event=None):
    canvas_1.pack_forget()
    button_1.pack_forget()
    button_2.pack() 
    button_3.pack()
    canvas_2.pack()
    
def show_canvas_3(event=None):
    canvas_2.pack_forget()
    button_2.pack_forget()
    canvas_3.pack()
    
#close window by pressing anywhere within window (canvas)
def close_app(event):
    root.destroy()

root = Tk()
root.title("Belladonna")

#create canvas windows
canvas_1 = Canvas(root, width=800, height=800, bg="red")
canvas_2 = Canvas(root, width=800, height=800, bg="green")
canvas_3 = Canvas(root, width=800, height=800, bg="blue")

#create buttons
button_1 = Button(root, text="start", command=show_canvas_2)
button_2 = Button(root, text="back", command=show_canvas_1)
button_3 = Button(root, text="end", command=show_canvas_3)

canvas_1.bind("<Button-1>", show_canvas_2) #make canvas button
canvas_2.bind("<Button-1>", show_canvas_3)
canvas_3.bind("<Button-1>", close_app)

#organise elements (widgets)
button_1.pack()
canvas_1.pack()

#create a point
point = canvas_2.create_oval(390, 390, 400, 400, fill="blue")
direction = 'right' #add direction

move_point() #move point

root.mainloop()