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


listPort = []
listBaudRate = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]


# ******************************************************************************************************************
# PageOne of UI  
# ******************************************************************************************************************
class UI(QWidget):
    def __init__(self):
        super().__init__()
        
        # *********************************************************
        # Load and setting the default when opening the GUI
        # *********************************************************
        loadUi('design_ui/tmp.ui', self)
        self.setWindowTitle('QuocBrave')

        # *********************************************************
        # Creating class elements for UI
        # *********************************************************
        # Creating class serial
        self.ser = SerialComm()

        # Creating class user information
        self.user = UserInfor()

        # *********************************************************
        # setting the visible elements 
        # *********************************************************
        self.groupBoxConnection.setVisible(True)
        self.gbxUserData.setVisible(False) 
        self.gbxImageID.setVisible(False)

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
        self.btnScanUart.clicked.connect(self.addComPortBaudrate) 
        self.btnConnectUart.clicked.connect(self.connectComport)

        # For User Data
        self.btnUserData.clicked.connect(self.userData)
        self.btnClearUserData.clicked.connect(self.clearDataUser)

        # For register / Edit user data
        self.btnEditData.clicked.connect(self.registerUserData)
        self.btnScanUser.clicked.connect(self.scanTagsUserRegister)
        self.btnImagePath.clicked.connect(self.browseImageUser)
        self.btnClrDataInput.clicked.connect(self.clearDisplayData)
        self.btnSaveUser.clicked.connect(self.saveRegisterUser)

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
        

        self.show()
        
# ******************************************************************************************************************
# ******************************************************************************************************************
    # add listport into ComboBox
    def addComPortBaudrate(self):
        # add comport
        listPort = self.ser.getPortNumber()
        print(listPort)
        for port in listPort:
            self.cbxScanPortUart.addItem(port)

        # add baudrate
        print(listBaudRate)
        for baudrate in listBaudRate:
            self.cbxBaudRateUart.addItem(str(baudrate))
        # setting default index
            self.cbxBaudRateUart.setCurrentIndex(4) 

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
                self.lbConnectImage.setPixmap(QPixmap('picture/image_tools/Connected.png'))
            else:
                self.flagBlinkConnect = True
                self.lbConnectImage.setPixmap(QPixmap(''))

# ******************************************************************************************************************
# ******************************************************************************************************************
    # connect to port from Combobox
    def connectComport(self):
        try:
            if self.flagConnect == False:
                comport = self.cbxScanPortUart.currentText()
                baurate = self.cbxBaudRateUart.currentText()
                print(comport)
                print(baurate)

                # connecting to port and baudrate
                self.ser.connectSerial(serialPort=comport, baudRate=baurate)
                self.btnConnectUart.setText('Disconnect')
                self.lbConnectionStatus.setText('Connection Status : Connected')
                self.lbConnectImage.setPixmap(QPixmap('picture/image_tools/Connected.png'))
                self.lbConnectImage.setScaledContents(True)
                self.flagConnect = True
                pass
            else:
                self.ser.closeSerial()
                self.btnConnectUart.setText('Connect')
                self.lbConnectionStatus.setText('Connection Status : Disconnected')
                self.lbConnectImage.setPixmap(QPixmap('picture/image_tools/Disconnect.png'))
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
        self.gbxUserData.setVisible(False) 
        self.gbxImageID.setVisible(False)

# =================================================================================================================
# Processing for user Data button
# =================================================================================================================
    def userData(self):
        if self.flagConnect:
            # setting multi-media for the  display 
            self.lb_select.setGeometry(-10, 390, 51, 61)
            self.groupBoxConnection.setVisible(True)
            self.gbxUserData.setVisible(True) 
            self.gbxImageID.setVisible(False)

            self.clearDataUser()

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
                        self.lbIDUser.setText('ID: ' + self.dataDisplay)

                    if self.user.checkDataFromDataBase():
                        #TODO: Display data user
                        pass
                    else:
                        pass

    def clearDataUser(self):
        self.lbDispName.setText('Waiting...')
        self.lbDispAddress.setText('Waiting...')
        self.lbDispCity.setText('Waiting...')
        self.lbDispCountry.setText('Waiting...')
        self.lbIDUser.setText('ID :_______________________')

# =================================================================================================================
# Processing for Register / Edit User
# =================================================================================================================
    def registerUserData(self):
        if self.flagConnect:
            # setting multi-media for the display 
            self.lb_select.setGeometry(-10, 460, 51, 61)
            self.groupBoxConnection.setVisible(True)
            self.gbxUserData.setVisible(True) 
            self.gbxImageID.setVisible(True)
            
            self.lbReadLoading.setVisible(False)  
            self.grapViewImgLoading.setVisible(False)
            self.btnCloseLoading.setVisible(False)
            self.lbWaitLoading.setVisible(False)

            self.clearDisplayData()
            self.rioSearchName.setChecked(True)

              #Row count 
            self.tableWidgetRecord.setRowCount(4)  
    
            #Column count 
            self.tableWidgetRecord.setColumnCount(2)   
    
            self.tableWidgetRecord.setItem(0,0, QTableWidgetItem("Name")) 
            self.tableWidgetRecord.setItem(0,1, QTableWidgetItem("City")) 
            self.tableWidgetRecord.setItem(1,0, QTableWidgetItem("Aloysius")) 
            self.tableWidgetRecord.setItem(1,1, QTableWidgetItem("Indore")) 
            self.tableWidgetRecord.setItem(2,0, QTableWidgetItem("Alan")) 
            self.tableWidgetRecord.setItem(2,1, QTableWidgetItem("Bhopal")) 
            self.tableWidgetRecord.setItem(3,0, QTableWidgetItem("Arnavi")) 
            self.tableWidgetRecord.setItem(3,1, QTableWidgetItem("Mandsaur")) 



            self.flagRegister = True
            self.flagUserData = False
            self.semaphoreRegister.release()


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
        self.lbReadLoading.setVisible(True)  
        self.grapViewImgLoading.setVisible(True)
        self.btnCloseLoading.setVisible(True)
        self.lbWaitLoading.setVisible(True)

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
                    self.lbReadLoading.setVisible(False)  
                    self.grapViewImgLoading.setVisible(False)
                    self.btnCloseLoading.setVisible(False)
                    self.lbWaitLoading.setVisible(False)

                    # Processing receive data
                    self.dataDisplay = ''
                    for i in range(len(receiveData)):
                        self.dataDisplay += '{0:x}'.format(receiveData[i])
                        self.lbIDRegister.setText('ID    ' + self.dataDisplay)


    def saveRegisterUser(self):
        # fetch the element data from UI
        self.user.name = self.txtName.toPlainText()
        self.user.address = self.txtAddress.toPlainText()
        self.user.city = self.txtCity.toPlainText()
        self.user.country = self.txtCountry.toPlainText()
        idRaw = self.lbIDRegister.text()
        lenIdRaw = len(idRaw)
        self.user.idUser = idRaw[6: lenIdRaw]

        print('user name: ', self.user.name)
        print('user address: ', self.user.address)
        print('user city: ', self.user.city)
        print('user country: ', self.user.country)
        print('id user: ', self.user.idUser)
        print('user imagepath: ', self.user.imageName)

        # check the conditions needs to save data of user, 
        # vice sersa will notify the administrator 
        if len(self.user.name) == 0 and len(self.user.address) == 0 \
            and len(self.user.city) == 0 and len(self.user.country) == 0:
            print("Not eligible for registration because the textbox yet fill out")
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please fill in the textbox completely!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
        elif self.user.idUser == 'ID    _________':
            print("Not eligible for registration because the id user yet scan") 
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please click the scan button to have the code tags!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
        
        elif len(self.user.imageName) == 0:
            print("Not eligible for registration because the browse choose the image yet ") 
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please click the scan browse to have the image of user!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
        else:
            print('the data user validated')
            # Save data to database
            self.user.saveData()

            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Data saved successfullly")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

            # Clear data for the next register
            self.clearDisplayData()

            # TODO: Display the data just saved on the table 

    def clearDisplayData(self):
        self.txtName.setText('')
        self.txtAddress.setText('')
        self.txtCity.setText('')
        self.txtCountry.setText('')
        self.lbIDRegister.setText('ID    _________')
        self.btnImagePath.setIconSize(self.btnImagePath.size())
        self.btnImagePath.setIcon(QtGui.QIcon('picture/image_tools/Click_to_browse.png'))
        self.user.imageName = ''

    def browseImageUser(self):
        # Choose the image file for the user data
        filename = QFileDialog.getOpenFileName()
        imagePath = filename[0]
        print(imagePath)
        self.user.imageName = os.path.split(imagePath)[-1]

        # display the image to button
        self.btnImagePath.setIconSize(self.btnImagePath.size())
        self.btnImagePath.setIcon(QtGui.QIcon(imagePath))


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
    sys.exit(app.exec_())