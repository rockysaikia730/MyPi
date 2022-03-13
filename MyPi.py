#----------------PyQT For GUI-------------------
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QStyle, QSizePolicy
import sys
from PyQt5.QtGui import QIcon, QPalette,QPixmap
from PyQt5.QtCore import Qt, QUrl, QThread, QObject, pyqtSignal
#------------Automation Libraries---------------
import pyautogui
import platform
from pynput.mouse import Button, Controller
#----------------------------------------------
import socket
from math import *
import time

#Default PAUSE value
pyautogui.PAUSE=0.0000001

#Device-Host and Client
max_width_device = 1920   
max_height_device = 1080

device_height = pyautogui.size()[1]
device_width = pyautogui.size()[0]

#Scale Factor for Device
scale_height = int(device_height/max_height_device)
scale_width = int(device_width/max_width_device)

#Mouse object
mouse = Controller()

#Loop Parameter
Done=False

#List Function
def reclist(listname,data):
    del listname[0]
    listname.append(data)

#Worker Thread  
class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

        #Initialization
        pos = pyautogui.position()
        #self.control = [x,y,mouse_wheel,left_press,right_press]
        self.control = [pos[0],pos[1],0,0,0] 
        #self.corarray = [(x,y),(x,y),(x,y),(x,y),(x,y)]
        self.corarray = [(pos[0]+i,pos[1]+i) for i in range(-2,3)] 
        #self.larray = [l1,l2,l3,l4,l5] List of Left_press value
        self.larray = [0,0,0,0,0]   
        
    #Stop Receiving from Socket
    def stop(self):
        global Done
        Done=False
    
    #Enable TCP Data Exchange
    def run(self):
        global s #socket
        global Done
        global BUFFER_SIZE #Bytes of Data Received
        try:
            while True:
                while Done:
                    #------Receiving Data
                    data =s.recv(BUFFER_SIZE).decode("utf-8")
                    x = data.split('.')
                    if len(x)==5 and x[0]!='':
                        for i in range(5):
                            self.control[i]=int(x[i])        

                    #-----------Record Previous left presses and coordinate data------------

                    reclist(self.larray,self.control[3]) #l1,l2,l3,l4,l5]
                    reclist(self.corarray,(self.control[0],self.control[1]))#corarray = [(x1,y1),(x2,y2),(x3,y3),(x4,y4),(x5,y5)]'''

                    #-------Move Cursor-------------
                    pyautogui.moveTo(scale_width*self.control[0],scale_width*self.control[1])

                    #-------------Scroll-------------
                    if self.control[2]:
                        pyautogui.scroll(self.control[2]*85)
                    #------Clicks--------------------
                    elif self.control[3] or self.control[4]:
                        #Double Left Click
                        if not(self.larray[-1]) and all(element==self.corarray[0] for element in self.corarray):
                            if self.larray[:-1] == [1,-1,1,-1]:
                                mouse.click(Button.left,2)
                        
                        
                        if self.control[3]==1:
                            #Left Press
                            mouse.press(Button.left)
                        
                        elif self.control[3] == -1:
                            #Left Release
                            mouse.release(Button.left)
                        
                        elif self.control[4]==1:
                            #Right Press
                            mouse.press(Button.right)
                        
                        elif self.control[4]==-1:
                            #Right Release
                            mouse.release(Button.right)

        except Exception as e:
            print(e)
            self.finished.emit()
 
#Main Window Control
class Window(QWidget):
    def __init__(self):
        super().__init__()

        #Window Object
        self.setWindowTitle("RASP MICE")
        self.setGeometry(350, 100, 300, 200)
      
 
        p =self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
 
        self.init_ui()
        self.show()
 
    def init_ui(self):
        

        #create connect button
        self.conntBtn = QPushButton('Connect')
        self.conntBtn.clicked.connect(self.connecttorasp)

        #create activate button
        self.actBtn = QPushButton('Activate')
        self.actBtn.resize(100,100)
        self.actBtn.setEnabled(False)
        self.actBtn.clicked.connect(self.fetchfromrasp)

        #create deactivate button
        self.deBtn = QPushButton('Deactivate')
        self.deBtn.setEnabled(False)
        self.deBtn.clicked.connect(self.deactivate)

        #create label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
 
        #create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0,0,0,0)
 
        #set widgets to the hbox layout
        hboxLayout.addWidget(self.conntBtn)

        #create hbox layout
        hboxLayout2 = QHBoxLayout()
        hboxLayout2.setContentsMargins(0,0,0,0)
        hboxLayout2.addWidget(self.actBtn)
        hboxLayout2.addWidget(self.deBtn)

        #create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addLayout(hboxLayout2)
        vboxLayout.addWidget(self.label)

        self.setLayout(vboxLayout)
 
    def connecttorasp(self):
        #Default TCP of Rasp Pi
        TCP_IP = '192.168.0.107'
        TCP_PORT = 5005

        #Buffer Size is 18 bytes : xxxx.yyyy.mw.ll.rr
        global BUFFER_SIZE
        BUFFER_SIZE = 18
       
        #Setting up Socket
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))

        #Initializing Threading
        self.thread =QThread()
        #Create a worker obejct
        self.worker = Worker()
        #move worker to the thread
        self.worker.moveToThread(self.thread)
        #Initiate connects
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        #Starting thread
        self.thread.start()
        #Enable activate button
        self.actBtn.setEnabled(True)

    def fetchfromrasp(self):
        #Executes data fetching and controls
        global Done
        Done=True

        #Toggle Buttons
        self.actBtn.setEnabled(False)
        self.deBtn.setEnabled(True)
       
    
    def deactivate(self):
        #Stop Data fetching
        self.worker.stop()

        #Toggle Button
        self.actBtn.setEnabled(True)
        self.deBtn.setEnabled(False)
    
 
app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())