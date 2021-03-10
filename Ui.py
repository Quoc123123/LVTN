import sys
import threading
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from smart_util import *
from serial_attendance import *
from user_infor import *
from face_attendance import *


listPort = []
listBaudRate = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

PATH_IMAGE_USER = 'picture/image_user/'
PATH_IMAGE_TOOLS = 'picture/image_tools/'
PATH_IMAGE_SAVE = 'picture/image_save/'




# ******************************************************************************************************************
# PageOne of UI  
# ******************************************************************************************************************
class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # *********************************************************
        # Load and setting the default when opening the GUI
        # *********************************************************
        loadUi('design_ui/Ui.ui', self)
        self.setWindowTitle('QuocBrave')

        # *********************************************************
        # Creating class elements for UI
        # *********************************************************
        # Creating class serial
        self.ser = SerialComm()

        # Creating class user information
        self.user = UserInfor()

        # Creating class face recognition
        self.faceRecognition = RecognitionUser()

        # *********************************************************
        # setting the visible elements 
        # *********************************************************
        self.groupBoxConnection.setVisible(True)
        self.groupBoxUserData.setVisible(False) 
        self.groupBoxImageID.setVisible(False)
        self.addComPortBaudrate()
        

        # *********************************************************
        # display time and date on UI
        # *********************************************************
        # creating a timer object
        timer = QTimer(self)
        
        # adding action to timer
        timer.timeout.connect(self.showDateTime)

        # update the timer every second 
        timer.start(1000)
    
        # **********************************************************
        # Event of button   
        # **********************************************************
        # For connection
        self.btnConnection.clicked.connect(self.connectionSetting)
        self.btnScanPort.clicked.connect(self.addComPortBaudrate) 
        self.btnConnect.clicked.connect(self.connectComport)

        # For User Data
        self.btnUserData.clicked.connect(self.userData)
        self.btnClear.clicked.connect(self.clearDataUser)

        # For register / Edit user data
        self.btnEditData.clicked.connect(self.registerUserData)
        self.btnScanRegister.clicked.connect(self.scanTagsUserRegister)
        self.btnBrowseImage.clicked.connect(self.browseImageUserAndTrain)
        self.btnClearDataInput.clicked.connect(self.clearDisplayData)
        self.btnSaveDataUser.clicked.connect(self.saveRegisterUser)

        # **********************************************************
        # Manage multiple threads
        # **********************************************************
        # Creating critical section to share counter objects
        self.mutexLock = threading.Lock()

        # Creating thread instance where count = 1
        self.semaphoreRegister = threading.Semaphore()
        self.semaphoreUserData = threading.Semaphore()

        self.flagConnect = False
        self.flagBlinkConnect = False

        self.flagRegister = False
        self.flagUserData = False

        self.name = ''
        self.idUser = ''
        self.address = ''
        self.city = ''
        self.country = ''
        self.timeRegister = ''
        self.imagePath = ''
        

        # show init UI
        self.show()
        
# ******************************************************************************************************************
# ******************************************************************************************************************
    # add listport into ComboBox
    def addComPortBaudrate(self):
        # add comport
        listPort = self.ser.getPortNumber()
        print(listPort)
        for port in listPort:
            self.cbxScanPort.addItem(port)

        # add baudrate
        print(listBaudRate)
        for baudrate in listBaudRate:
            self.cbxBaudRate.addItem(str(baudrate))
        # setting default index
            self.cbxBaudRate.setCurrentIndex(4) 

    def showDateTime(self):
        # get time from object QDateTime
        currentDateTime = QDateTime.currentDateTime()
        lbDateTime = currentDateTime.toString(Qt.DefaultLocaleLongDate) 
        
        # setting the layout to main window
        self.lbDateTime.setAlignment(Qt.AlignCenter)

        # display time to gui
        self.lbDateTime.setText(lbDateTime) 

        # setting blink for the connection
        if self.flagConnect:
            if self.flagBlinkConnect:
                self.flagBlinkConnect = False
                self.lbConnectImage.setPixmap(QPixmap(PATH_IMAGE_TOOLS + 'Connected.png'))
            else:
                self.flagBlinkConnect = True
                self.lbConnectImage.setPixmap(QPixmap(''))

# ******************************************************************************************************************
# ******************************************************************************************************************
    # connect to port from Combobox
    def connectComport(self):
        try:
            if self.flagConnect == False:
                comport = self.cbxScanPort.currentText()
                baurate = self.cbxBaudRate.currentText()
                print(comport)
                print(baurate)

                # connecting to port and baudrate
                self.ser.connectSerial(serialPort=comport, baudRate=baurate)
                self.btnConnect.setText('Disconnect')
                self.lbConnectionStatus.setText('Connection Status : Connected')
                self.lbConnectImage.setPixmap(QPixmap(PATH_IMAGE_TOOLS + 'Connected.png'))
                self.lbConnectImage.setScaledContents(True)
                self.flagConnect = True
                pass
            else:
                self.ser.closeSerial()
                self.btnConnect.setText('Connect')
                self.lbConnectionStatus.setText('Connection Status : Disconnected')
                self.lbConnectImage.setPixmap(QPixmap(PATH_IMAGE_TOOLS + 'Disconnect.png'))
                self.lbConnectImage.setScaledContents(True)
                self.flagConnect = False
                print('Closed serial port')
        except Exception as exc:
            print('Error creating serialDevice')
            msg = QMessageBox() 
            msg.setWindowTitle("Connect")
            msg.setText("Please select the port to connect!!!")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

# =================================================================================================================
# Processing for conection button
# =================================================================================================================
    def connectionSetting(self):
        self.lb_select.setGeometry(-10, 320, 51, 61)
        self.groupBoxConnection.setVisible(True)
        self.groupBoxUserData.setVisible(False) 
        self.groupBoxImageID.setVisible(False)

# =================================================================================================================
# Processing for user Data button
# =================================================================================================================
    def userData(self):
        self.clearDataUser()
        if self.flagConnect:
            # setting multi-media for the  display 
            self.lb_select.setGeometry(-10, 390, 51, 61)
            self.groupBoxConnection.setVisible(True)
            self.groupBoxUserData.setVisible(True) 
            self.groupBoxImageID.setVisible(False)

            self.flagRegister = False
            self.flagUserData = True
            self.semaphoreUserData.release()

            # Creating thread to scan data from the reader system
            self.threadScanTags = threading.Thread(target=self.scanTagsUserData, args=[])
            # Read card and commpare with previously stored data 
            self.threadScanTags.start()
        else:
            print("Not into user data mode if doesn't yet connect")
            msg = QMessageBox() 
            msg.setWindowTitle("information")
            msg.setText("Click the Connection menu then click the Connect button!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

    def scanTagsUserData(self):
        while True:
            self.semaphoreUserData.acquire()
            while self.flagUserData:
                # Enter into critical section
                self.mutexLock.acquire()

                checkData = self.ser.check_data_from_device()
                receiveData = self.ser.get_data_from_device()
                
                # Exit critical section
                self.mutexLock.release()

                if checkData > 0:
                    # Processing receive data
                    self.dataDisplay = ''
                    for i in range(len(receiveData)):
                        self.dataDisplay += '{0:x}'.format(receiveData[i])
                        self.lbIDUserData.setText('ID: ' + self.dataDisplay)

                    id = self.lbIDUserData.text()[4:]
                    if self.user.checkDataUser(id) == mysql_query_status['USER_EXIST']:
                        ls = self.user.getDataUser(id)
                        self.lbDisplayName.setText(ls[0])
                        self.lbIDUserData.setText('ID: ' + ls[1])
                        self.lbDisplayAddress.setText(ls[2])
                        self.lbDisplayCity.setText(ls[3])
                        self.lbDisplayCountry.setText(ls[4])
                        self.lbViewUser.setScaledContents(True)
                        self.lbViewUser.setPixmap(QPixmap(ls[6]))

                    else:
                        pass
                        #TODO: Display the message user doesn't register yet

    def clearDataUser(self):
        self.lbDisplayName.setText('Waiting...')
        self.lbDisplayAddress.setText('Waiting...')
        self.lbDisplayCity.setText('Waiting...')
        self.lbDisplayCountry.setText('Waiting...')
        self.lbIDUserData.setText('ID :_______________________')
        self.lbViewUser.setPixmap(QPixmap(''))

# =================================================================================================================
# Processing for Register / Edit User
# =================================================================================================================
    def registerUserData(self):
        if self.flagConnect:
            # setting multi-media for the display 
            self.lb_select.setGeometry(-10, 460, 51, 61)
            self.groupBoxConnection.setVisible(True)
            self.groupBoxUserData.setVisible(True) 
            self.groupBoxImageID.setVisible(True)
            
            self.lbReadingTag.setVisible(False)  
            self.grapViewImgReadingTag.setVisible(False)
            self.btnCloseTag.setVisible(False)
            self.lbLoading.setVisible(False)

            self.clearDisplayData()
            self.radioSearchName.setChecked(True)

            # Row count 
            self.tableWidget.setRowCount(4)  
    
            # Column count 
            self.tableWidget.setColumnCount(6)   
    
            self.tableWidget.setItem(0, 0, QTableWidgetItem("Name")) 
            self.tableWidget.setItem(0, 1, QTableWidgetItem("ID")) 
            self.tableWidget.setItem(0, 2, QTableWidgetItem("Address")) 
            self.tableWidget.setItem(0, 3, QTableWidgetItem("City")) 
            self.tableWidget.setItem(0, 4, QTableWidgetItem("Country"))
            self.tableWidget.setItem(0, 5, QTableWidgetItem("Time"))

            # Table will fit the screen horizontally 
            self.tableWidget.horizontalHeader().setStretchLastSection(True) 
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  

            self.flagRegister = True
            self.flagUserData = False
            
        else:
            print("Not into Register/Edit User data mode if doesn't yet connect")
            msg = QMessageBox() 
            msg.setWindowTitle("information")
            msg.setText("Click the Connection menu then click the Connect button!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

    def scanTagsUserRegister(self):
        try:
            # check the status if connected else message box pop not connected 
            if self.flagConnect:
                # creating the thread for both animation and receive the data within wating the scan tags
                threadReceivedDataFromReader = threading.Thread(target=self.receivedDataFromReader, args=[5])
                threadReceivedDataFromReader.start()
            else:
                threadMessages = threading.Thread(target=speakMessage, args=('Error, please connect again', 1, 1, 1))
                threadMessages.start()
        except:
            print('Cannot scan rfid card')
            msg = QMessageBox() 
            msg.setWindowTitle("Warning")
            msg.setText("Cannot scan rfid card!!!")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message 

    def receivedDataFromReader(self, timeout):
        self.lbReadingTag.setVisible(True)  
        self.grapViewImgReadingTag.setVisible(True)
        self.btnCloseTag.setVisible(True)
        self.lbLoading.setVisible(True)

        self.semaphoreRegister.release()
        
        start_time = time.time()
        while True:
            # calling accquire method
            self.semaphoreRegister.acquire()
            while self.flagRegister:
                self.mutexLock.acquire()
                checkData = self.ser.check_data_from_device()
                receiveData = self.ser.get_data_from_device()
                # Exit critical section
                self.mutexLock.release()

                if checkData > 0:
                    # Disable lable loading
                    self.lbReadingTag.setVisible(False)  
                    self.grapViewImgReadingTag.setVisible(False)
                    self.btnCloseTag.setVisible(False)
                    self.lbLoading.setVisible(False)

                    # Processing receive data
                    self.dataDisplay = ''
                    for i in range(len(receiveData)):
                        self.dataDisplay += '{0:x}'.format(receiveData[i])
                        self.lbID.setText('ID    ' + self.dataDisplay)

                    idRaw = self.lbID.text()
                    lenIdRaw = len(idRaw)
                    self.idUser = idRaw[6: lenIdRaw]
                    
            # Disable lable loading
            self.lbReadingTag.setVisible(False)  
            self.grapViewImgReadingTag.setVisible(False)
            self.btnCloseTag.setVisible(False)
            self.lbLoading.setVisible(False)

    def saveRegisterUser(self):
        # fetch the element data from UI
        self.name = self.textName.toPlainText()
        self.address = self.textAddress.toPlainText()
        self.city = self.textCity.toPlainText()
        self.country = self.textCountry.toPlainText()
        self.timeRegister = get_current_time()

        
        print('user name: ', self.name)
        print('user address: ', self.address)
        print('user city: ', self.city)
        print('user country: ', self.country)
        print('id user: ', self.idUser)
        print('current_time', self.timeRegister)
        print('user imagepath: ', self.imagePath)

        # check the conditions needs to save data of user, 
        # vice sersa will notify the administrator 
        if self.idUser == 'ID    _________':
            print("Not eligible for registration because the id user yet scan") 
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please click the scan button to have the code tags!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
        else:
            # Check the data exits or not 
            status = self.user.checkDataUser(self.idUser)
            if  status == mysql_query_status['USER_EXIST']:
                # User exists
                msg = QMessageBox() 
                msg.setWindowTitle("Information")
                msg.setText("User registered, do you want to edit the data ?")
                msg.setIcon(QMessageBox.Question)
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.Yes)
                x = msg.exec_() # execute the message
                if x == QMessageBox.Yes:
                    pass    
                    # TODO: Edit data on database
            else:
                # User doest't register yet
                if len(self.name) == 0 and len(self.address) == 0 \
                    and len(self.city) == 0 and len(self.country) == 0:
                    print("Not eligible for registration because the textbox yet fill out")
                    msg = QMessageBox() 
                    msg.setWindowTitle("Information")
                    msg.setText("Please fill in the textbox completely!!!")
                    msg.setIcon(QMessageBox.Information)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    x = msg.exec_() # execute the message

                elif self.idUser == 'ID    _________':
                    print("Not eligible for registration because the id user yet scan") 
                    msg = QMessageBox() 
                    msg.setWindowTitle("Information")
                    msg.setText("Please click the scan button to have the code tags!!!")
                    msg.setIcon(QMessageBox.Information)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    x = msg.exec_() # execute the message
        
                elif len(self.imagePath) == 0:
                    print("Not eligible for registration because the browse choose the image yet ") 
                    msg = QMessageBox() 
                    msg.setWindowTitle("Information")
                    msg.setText("Please click the scan browse to have the image of user!!!")
                    msg.setIcon(QMessageBox.Information)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    x = msg.exec_() # execute the message

                else:
                    # User does't register yet
                    status = self.user.insertData(self.name, self.idUser, self.address, self.city, self.country,self.timeRegister, self.imagePath)
                    if status == mysql_query_status['INSET_OK']:
                        msg = QMessageBox() 
                        msg.setWindowTitle("Information")
                        msg.setText("Data saved successfullly")
                        msg.setIcon(QMessageBox.Information)
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.setDefaultButton(QMessageBox.Ok)
                        x = msg.exec_() # execute the message

                        # Clear data for the next register
                        self.clearDisplayData()
                        # TODO: Display the data just inserted on the table 
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('Data failed')
                        msg.setInformativeText('Data failed to save')
                        msg.setWindowTitle("Error")
                        x = msg.exec_()

    def clearDisplayData(self):
        self.textName.setText('')
        self.textAddress.setText('')
        self.textCity.setText('')
        self.textCountry.setText('')
        self.lbID.setText('ID    _________')
        self.btnBrowseImage.setIconSize(self.btnBrowseImage.size())
        self.btnBrowseImage.setIcon(QtGui.QIcon(PATH_IMAGE_TOOLS + 'Click_to_browse.png'))
        self.imagePath = ''

    def browseImageUserAndTrain(self):
        # # Choose the image file for the user data
        # filename = QFileDialog.getOpenFileName()
        # self.imagePath = filename[0]
        # print(self.imagePath)
        # # self.imagePath = os.path.split(imagePath)[-1]

        if self.lbID.text() == 'ID    _________':
            print("Not eligible for registration because the id user yet scan") 
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please click the scan button to have the code tags!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
        else:
            self.imagePath = self.faceRecognition.getDataSet(self.idUser)

            # display the image to button
            self.btnBrowseImage.setIconSize(self.btnBrowseImage.size())
            self.btnBrowseImage.setIcon(QtGui.QIcon(self.imagePath))
            



    def clearDisplayTable(self):
        self.tableWidget.clear()


# =================================================================================================================
# Run the UI
# =================================================================================================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    ui = UI()
    # widget = QtWidgets.QStackedWidget() # to switch the sceens in the case you have many windows 
    # widget.addWidget(ui)
    # widget.setFixedWidth(1138)
    # widget.setFixedHeight(844)
    # widget.show()
    sys.exit(app.exec_())