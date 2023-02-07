from tkinter import *

#point moves left to right repeatedly
def move_point():
    global direction #access global variable
    if direction == 'right':
        canvas.move(point, -5, 0) #move point 5 pixels to the left
        if canvas.coords(point)[0] < 0:  #check coordinates
            direction = 'left'
    else:
        canvas.move(point, 5, 0) #move point 5 pixels to the right
        if canvas.coords(point)[2] > 800: #check coordinates
            direction = 'right'
    canvas.after(50, move_point) #update canvals every 50ms
    
#close window by pressing anywhere within window (canvas)
def close_app(event):
    print(event)
    root.destroy()

root = Tk()
root.title("Belladonna")

#create canvas window
canvas = Canvas(root, width=800, height=800)
canvas.pack() #organise elements (widgets)

canvas.bind("<Button-1>", close_app) #make canvas button

#create a dot
point = canvas.create_oval(390, 390, 400, 400, fill="blue")
direction = 'right'

move_point()

root.mainloop()