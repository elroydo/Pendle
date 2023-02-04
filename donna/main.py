from tkinter import *

def move_point():
    canvas.move(point, 5, 0) #move point 5 pixels to the right
    canvas.after(50, move_point) #update canvals every 50ms

root = Tk()
root.title("Belladonna")

#create canvas window
canvas = Canvas(root, width=800, height=800)
canvas.pack() #organise elements (widgets) 

#create a dot
point = canvas.create_oval(390, 390, 400, 400, fill="blue")

move_point()

root.mainloop()