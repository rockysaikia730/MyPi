import socket
from pynput import mouse
import time


TCP_IP = '0.0.0.0' #To look for any available IP address
TCP_PORT = 5005
BUFFER_SIZE = 18
o=[0,0,0,0,0]#x,y,mouse wheel,left,right

#Connecting the socket via interent
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print ('Connection address:', addr)


def on_move(x, y):
    #Gets the Position of mouse cursor 
    o[0],o[1]=x,y
    o[2]=0
    if o[3]==1:
        o[3]=1
    else:
        o[3]=0
    if o[4]==1:
        o[4]=1
    else:
        o[4]=0
    #Sends the data to client in form of string
    x=bytes((f'{o[0]:0004d}'+"."+f'{o[1]:0004d}'+"."+f'{o[2]:+2d}'+"."+f'{o[3]:+2d}'+"."+f'{o[4]:+2d}').encode("utf-8"))
    conn.send(x)
   
def on_click(x, y, button, pressed):
    #Looks for right click and left click
    if button == mouse.Button.left:
        if pressed== True:
            o[3]=1
            o[4]=0
        else:
            o[3]=-1
            o[4]=0
    if button == mouse.Button.right:
        if pressed== True:
            o[4]=1
            o[3]=0
        else:
            o[3]=0
            o[4]=-1
    o[2]=0

    ##Sends the data to client in form of string
    x=bytes((f'{o[0]:0004d}'+"."+f'{o[1]:0004d}'+"."+f'{o[2]:+2d}'+"."+f'{o[3]:+2d}'+"."+f'{o[4]:+2d}').encode("utf-8"))
    conn.send(x)

    
def on_scroll(x, y, dx, dy):
    #Looks for activity of mouse wheel
    o[2]=dy
    if o[3]==1:
        o[3]=1
    else:
        o[3]=0
    if o[4]==1:
        o[4]=1
    else:
        o[4]=0

    #Sends the data to client in form of string
    x=bytes((f'{o[0]:0004d}'+"."+f'{o[1]:0004d}'+"."+f'{o[2]:+2d}'+"."+f'{o[3]:+2d}'+"."+f'{o[4]:+2d}').encode("utf-8"))
    conn.send(x)

    
# Collect events until released
with mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll) as listener:
    listener.join()
    


# ...or, in a non-blocking fashion:
listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)
listener.start()


conn.close()



