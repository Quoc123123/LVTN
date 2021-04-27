# from serial_attendance import *



# ser = SerialComm()
# ser.connectSerial("/dev/ttyUSB0", 19200)
# # ser.pc_send_data_to_device(RFID_REQ_MSG_ID,[0x00])
# while 1:
#     a, data = ser.get_data_from_device()
#     print(data)


# print(len(a))
# print('{0:x}'.format(a[0]) + '{0:x}'.format(a[1]) + '{0:x}'.format(a[2]) + '{0:x}'.format(a[3]) + '{0:x}'.format(a[4]))



# import time
# import threading


# start = time.perf_counter()
# print('start: ', start)


# def do_something(seconds):
#     print(f'Sleeping {seconds} second(s) ... ')
#     time.sleep(seconds)
#     print('Done Sleeping ..  ')

# threads = []

# for _ in range(10):
#     t = threading.Thread(target=do_something, args=[1.5])
#     t.start()
#     threads.append(t)

# for thread in threads:
#     thread.join()


# finish = time.perf_counter()
# print('stop: ', finish)

# print(f'Finished in {round(finish - start, 2)} second(s)')





# # importing required librarie 
# import sys 
# from PyQt5.QtWidgets import QApplication, QWidget 
# from PyQt5.QtWidgets import QVBoxLayout, QLabel 
# from PyQt5.QtGui import QFont 
# from PyQt5.QtCore import QTimer, QTime, QDate, QDateTime, Qt 
  
  
# class Window(QWidget): 
  
#     def __init__(self): 
#         super().__init__() 
  
#         # setting geometry of main window 
#         self.setGeometry(100, 100, 800, 400) 
  
#         # creating a vertical layout 
#         layout = QVBoxLayout() 
  
#         # creating font object 
#         font = QFont('Arial', 120, QFont.Bold) 
  
#         # creating a label object 
#         self.label = QLabel() 
  
#         # setting centre alignment to the label 
#         self.label.setAlignment(Qt.AlignCenter) 
  
#         # setting font to the label 
#         self.label.setFont(font) 
  
#         # adding label to the layout 
#         layout.addWidget(self.label) 
  
#         # setting the layout to main window 
#         self.setLayout(layout) 
  
#         # creating a timer object 
#         timer = QTimer(self) 
  
#         # adding action to timer 
#         timer.timeout.connect(self.showTime) 
  
#         # update the timer every second 
#         timer.start(1000) 
  
#     # method called by timer 
#     def showTime(self): 
  
#         # getting current time 
#         current_time = QDateTime.currentDateTime()

#         # converting QTime object to string 
#         label_time = current_time.toString(Qt.DefaultLocaleLongDate) 
  
#         # showing it to the label 
#         self.label.setText(label_time) 
  
  
# # create pyqt5 app 
# App = QApplication(sys.argv) 
  
# # create the instance of our Window 
# window = Window() 
  
# # showing all the widgets 
# window.show() 
  
# # start the app 
# App.exit(App.exec_())



# # from queue import Queue 
# from threading import Thread 
# import time
  
# # A thread that produces data 
# def producer(out_q): 
#     while True: 
#         # Produce some data 
#         out_q.put('Quoc') 
          
# # A thread that consumes data 
# def consumer(in_q): 
#     while True: 
#         # Get some data 
#         data = in_q.get() 
#         # Process the data 
#         print(data)
#         # Indicate completion
#         in_q.task_done()
          
# # Create the shared queue and launch both threads 
# q = Queue() 
# t1 = Thread(target = consumer, args =(q, )) 
# t2 = Thread(target = producer, args =(q, )) 
# # t1.start() 
# # t2.start() 


# # Wait for all produced items to be consumed 
# q.join() 




# import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QFileDialog, QAction
# from PyQt5.QtGui import QIcon, QPixmap

# class MainWindow(QMainWindow):

#     def __init__(self, parent = None):
#         super(MainWindow, self).__init__(parent)

#         menubar = self.menuBar()
#         fileMenu = menubar.addMenu('File')
#         editMenu = menubar.addMenu('Edit')
#         self.resize(500, 500)

#         dlg = QFileDialog(self)       
#         openAction = QAction('Open Image', self)  
#         openAction.triggered.connect(self.openImage) 
#         fileMenu.addAction(openAction)

#         closeAction = QAction('Exit', self)  
#         closeAction.triggered.connect(self.close) 
#         fileMenu.addAction(closeAction)



#     def openImage(self):
#     # This function is called when the user clicks File->Open Image.
#         label = QLabel(self)
#         filename = QFileDialog.getOpenFileName()
#         imagePath = filename[0]
#         print(imagePath)
#         pixmap = QPixmap(imagePath)
#         label.setPixmap(pixmap)
#         self.resize(pixmap.width(),pixmap.height())
#         self.show()



# def main():
#     app = QApplication(sys.argv)
#     win = MainWindow()
#     win.show()
#     app.exec_()

# if __name__ == '__main__':
#     sys.exit(main()) 



# import os

# s = "D:/Study/Tren_lop/DeCuongLuanVan/UI/Attendance_System/picture/image_tools/icon_pen.png"
# print (os.path.split(s)[-1])
# print(os.path.basename(s))




# import sys 
# from PyQt5.QtWidgets import * 
                    
   
# #Main Window 
# class App(QWidget): 
#     def __init__(self): 
#         super().__init__() 
#         self.title = 'PyQt5 - QTableWidget'
#         self.left = 0
#         self.top = 0
#         self.width = 300
#         self.height = 200
   
#         self.setWindowTitle(self.title) 
#         self.setGeometry(self.left, self.top, self.width, self.height) 
   
#         self.createTable() 
   
#         self.layout = QVBoxLayout() 
#         self.layout.addWidget(self.tableWidget) 
#         self.setLayout(self.layout) 
   
#         #Show window 
#         self.show() 
   
#     #Create table 
#     def createTable(self): 
#         self.tableWidget = QTableWidget() 
  
#         #Row count 
#         self.tableWidget.setRowCount(4)  
  
#         #Column count 
#         self.tableWidget.setColumnCount(2)   
  
#         self.tableWidget.setItem(0,0, QTableWidgetItem("Name")) 
#         self.tableWidget.setItem(0,1, QTableWidgetItem("City")) 
#         self.tableWidget.setItem(1,0, QTableWidgetItem("Aloysius")) 
#         self.tableWidget.setItem(1,1, QTableWidgetItem("Indore")) 
#         self.tableWidget.setItem(2,0, QTableWidgetItem("Alan")) 
#         self.tableWidget.setItem(2,1, QTableWidgetItem("Bhopal")) 
#         self.tableWidget.setItem(3,0, QTableWidgetItem("Arnavi")) 
#         self.tableWidget.setItem(3,1, QTableWidgetItem("Mandsaur")) 
   
#         #Table will fit the screen horizontally 
#         self.tableWidget.horizontalHeader().setStretchLastSection(True) 
#         self.tableWidget.horizontalHeader().setSectionResizeMode( 
#             QHeaderView.Stretch) 
   
# if __name__ == '__main__': 
#     app = QApplication(sys.argv) 
#     ex = App() 
#     sys.exit(app.exec_()) 



# import MySQLdb
# from datetime import datetime
# dbConn=MySQLdb.connect("127.0.0.1","root","mobile","emp_attendance")or die("couldn't connect to DB")
# emp_name=input("Enter your name: ")
# emp_email=input("Enter your email: ")
# emp_pass=input("Enter validation text: ")
# emp_adr=input("Enter Address: ")
# emp_con=input("Enter Contact Number: ")
# month="%02d"%datetime.now().month
# day="%02d"%datetime.now().day
# emp_date=str(datetime.now().year)+"-"+month+"-"+day
# emp_rfid=raw_input("Enter given rfid number: ")
# emp_rfid=" "+emp_rfid
# cursor=dbConn.cursor()
# cursor.execute("Select * from employee_dat where email=(%s)",(emp_email))
# result=cursor.fetchall()
# x=int(cursor.rowcount)
# if(x!=0):
#     print "User already exists"
# else:
    
#     cursor.execute("insert into employee_dat (emp_name,emp_pass,email,contact,emp_add,join_date,rfid_num) values (%s,%s,%s,%s,%s,%s,%s)",(emp_name,emp_pass,emp_email,emp_con,emp_adr,emp_date,emp_rfid))
#     cursor.execute("select emp_id from employee_dat where email=(%s)",(emp_email))
#     result=cursor.fetchone()
#     result=str(result[0])
#     qry="create table %s(serial int(5) AUTO_INCREMENT NOT NULL PRIMARY KEY,mon_yr varchar(6))"%(result+"_attn_mo")
#     cursor.execute(qry)
# dbConn.commit()
# cursor.close()

# from user_infor import *

# test = UserInfor()

 
# test.selectTable()
# test.sortTable(table_columns_elements[1])
# test.updateUser('2244991', 'Name', 'abcd')
# print(test.getNumberUser())
# test.checkDataUser('123')'



# test.getDataUser('1122f1')





# # importing the required libraries 
  
# from PyQt5.QtWidgets import * 
# from PyQt5.QtCore import Qt 
# from PyQt5.QtGui import * 
# import sys 
  
# class Window(QMainWindow): 
#     def __init__(self): 
#         super().__init__() 
  
#         # set the title 
#         self.setWindowTitle("Label") 
  
#         # setting  the geometry of window 
#         self.setGeometry(0, 0, 650, 400) 
  
#         # creating a label widget and setting properties 
#         self.label_1 = QLabel("Bottom", self) 
#         self.label_1.move(20, 100) 
#         self.label_1.resize(60, 60) 
#         self.label_1.setStyleSheet("border: 1px solid black;") 
  
#         # aligning label to the bottom 
#         self.label_1.setAlignment(Qt.AlignBottom) 
  
#         # creating a label widget and setting properties 
#         self.label_2 = QLabel("Center", self) 
#         self.label_2.move(90, 100) 
#         self.label_2.resize(60, 60) 
#         self.label_2.setStyleSheet("border: 1px solid black;") 
  
#         # aligning label to the center 
#         self.label_2.setAlignment(Qt.AlignCenter) 
  
#         # creating a label widget and setting properties 
#         self.label_3 = QLabel("Left", self) 
#         self.label_3.move(160, 100) 
#         self.label_3.resize(60, 60) 
#         self.label_3.setStyleSheet("border: 1px solid black;") 
  
#         # aligning label to the left 
#         self.label_3.setAlignment(Qt.AlignLeft) 
  
#         # creating a label widget and setting properties 
#         self.label_4 = QLabel("Right", self) 
#         self.label_4.move(230, 100) 
#         self.label_4.resize(60, 60) 
#         self.label_4.setStyleSheet("border: 1px solid black;") 
  
#         # aligning label to the right 
#         self.label_4.setAlignment(Qt.AlignRight) 
  
#         # creating a label widget and setting properties 
#         self.label_5 = QLabel("Top", self) 
#         self.label_5.move(300, 100) 
#         self.label_5.resize(60, 60) 
#         self.label_5.setStyleSheet("border: 1px solid black;") 
  
#         # aligning label to the top 
#         self.label_5.setAlignment(Qt.AlignTop) 
  
#         # creating a label widget and setting properties 
#         self.label_6 = QLabel("H center", self) 
#         self.label_6.move(370, 100) 
#         self.label_6.resize(60, 60) 
#         self.label_6.setStyleSheet("border: 1px solid black;") 
  
#         # aligning label to the Hcenter 
#         self.label_6.setAlignment(Qt.AlignHCenter) 
  
#         # creating a label widget and setting properties 
#         self.label_7 = QLabel("V center", self) 
#         self.label_7.move(440, 100) 
#         self.label_7.resize(60, 60) 
#         self.label_7.setStyleSheet("border: 1px solid black;") 
  
#         # aligning label to the Vcenter 
#         self.label_7.setAlignment(Qt.AlignVCenter) 
  
#         # show all the widgets 
#         self.show() 
  
  
# # create pyqt5 app 
# App = QApplication(sys.argv) 
  
# # create the instance of our Window 
# window = Window() 
  
# # start the app 
# sys.exit(App.exec()) 


# from face_recogniton_knn import *
# import time

# test = RecognitionUser()


# test.getDataSet('987654321')
# test.trainingUser()
# a = test.recognitionUser()
# print(a)
# print(type(a[0]))
# print(type(a[1]))
# import cv2

# url = 'http://192.168.1.3:4747/video'

# video = cv2.VideoCapture(0)

# while True:
#     ret, frame = video.read()
#     if ret == True:
#         cv2.imshow('IPCam', frame)
#     if cv2.waitKey(1) == ord('q'):
#         break


# a = 925423848037


# print(str(1234))

# a = 'd7778f4a65'

# print('')

# import logging 
  
# #Create and configure logger 
# logging.basicConfig(filename="newfile.log", 
#                     format='%(asctime)s %(message)s', 
#                     filemode='w') 
  
# #Creating an object 
# logger=logging.getLogger() 
  
# #Setting the threshold of logger to DEBUG 
# logger.setLevel(logging.DEBUG) 
  
# #Test messages 
# logger.debug("Harmless debug Message") 
# logger.info("Just an information") 
# logger.warning("Its a Warning") 
# logger.error("Did you try to divide by zero") 
# logger.critical("Internet is down") 

# import datetime
# import time
# import os

# import pandas as pd

# col_names = ['Id', 'Name', 'Date', 'Time']
# attendance = pd.DataFrame(columns=col_names)

# # ts = time.time()
# # date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
# # timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
# attendance.loc[len(attendance)] = ['1', '2','3', '4']


# ts = time.time()
# date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
# timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
# Hour, Minute, Second = timeStamp.split(":")
# fileName = "Attendance"+os.sep+"Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
# attendance.to_csv(fileName, index=False)
# from user_infor import *

# test = UserInfor()
# # test.getNumberUser()
# test.getAllUser()
# # test.getDataUser('2244991')


# import datetime
 
# today = datetime.datetime.today()
# print(f"{today:%B %d, %Y}")


# from smart_util import *

# # csv_data_logging('quopc', '1232', 'bentre', 'hcm', 'vn')
# sendEmailToAdmin()


from face_recogniton_knn import *


abc = RecognitionUser()
# abc.facial_landmarks('456')
# abc.trainingUser()
print(abc.recognitionUser())

# import cv2

# url = 'http://192.168.1.3:4747/video'

# video = cv2.VideoCapture(url)

# import sys
# import glob
# import serial




# def serial_ports():
#     if sys.platform.startswith('win'):
#             ports = ['COM%s' % (i + 1) for i in range(256)]
#     elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
#         # this excludes your current terminal "/dev/tty"
#         ports = glob.glob('/dev/tty[A-Za-z]*')
#         print('ports: ', ports)
#     elif sys.platform.startswith('darwin'):
#         ports = glob.glob('/dev/tty.*')
#     else:
#         raise EnvironmentError('Unsupported platform')

#     result = []
#     for port in ports:
#         try:
#             s = serial.Serial(port)
#             s.close()
#             result.append(port)
#         except (OSError, serial.SerialException):
#             pass
#         return result

# if __name__ == '__main__':
#     print(serial_ports())

# from user_infor import *


# abc = UserInfor()
# abc.mysqlConnection()

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
import time
  
class LoadingGif(object):
  
    def mainUI(self, FrontWindow):
        FrontWindow.setObjectName("FTwindow")
        FrontWindow.resize(320, 300)
        self.centralwidget = QtWidgets.QWidget(FrontWindow)
        self.centralwidget.setObjectName("main-widget")
  
        # Label Create
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(25, 25, 200, 200))
        self.label.setMinimumSize(QtCore.QSize(250, 250))
        self.label.setMaximumSize(QtCore.QSize(250, 250))
        self.label.setObjectName("lb1")
        FrontWindow.setCentralWidget(self.centralwidget)
  
        # Loading the GIF
        self.movie = QMovie('picture/image_tools/' + "3.jpg")
        self.label.setMovie(self.movie)
  
        self.startAnimation()
  
  
    # Start Animation
  
    def startAnimation(self):
        self.movie.start()
  
    # Stop Animation(According to need)
    def stopAnimation(self):
        self.movie.stop()
  
  
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()
demo = LoadingGif()
demo.mainUI(window)
window.show()
sys.exit(app.exec_())


