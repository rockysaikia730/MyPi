
from tkinter import *

#Create an instance of Tkinter frame
win = Tk()

#Set the geometry
#Default Resolution of Raspberry Pi
win.geometry("1920x1080")

#Create a fullscreen window
win.attributes('-fullscreen', True)

win.mainloop()
