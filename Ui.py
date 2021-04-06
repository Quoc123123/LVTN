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
from face_recogniton_knn import *


listPort = []
listBaudRate = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

PATH_IMAGE_USER = 'picture/image_user/'
PATH_IMAGE_TOOLS = 'picture/image_tools/'
PATH_IMAGE_SAVE = 'picture/image_save/'

DATASET_TRAINING_PATH = 'recognition/dataset/'


infor_user = {
    'Name'              : 0,
    'ID'                : 1,
    'Address'           : 2,
    'City'              : 3,
    'Country'           : 4,
    'Time'              : 5,
    'Images'            : 6,
}



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
        self.setWindowTitle('Attendance System')

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
        
        self.btnFaceRecognition.clicked.connect(self.recognitionUser)
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

        self.flagUpdate = False

        self.name = ''
        self.idUser = ''
        self.address = ''
        self.city = ''
        self.country = ''
        self.timeRegister = ''
        self.imagePath = ''

        
        # The variable contains the amount of data registerd 
        self.numUserRegister = 0

        # show init UI
        self.show()
        
# =================================================================================================================
# Utils for the display
# =================================================================================================================
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
            
            # set default that using card to recognition user
            self.radioUsingCard.setChecked(True)

        else: 
            print("Not into user data mode if doesn't yet connect")
            msg = QMessageBox() 
            msg.setWindowTitle("information")
            msg.setText("Click the Connection menu then click the Connect button!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

    def recognitionUser(self):
        if self.radioUsingCard.isChecked():
            self.scanTagsUserData(5)
        else:
            self.usingFaceRecogniton()
    
    def usingFaceRecogniton(self):
        ret = self.faceRecognition.recognitionUser()
        if not ret[0]:
            #TODO: Display on ui which was failed
            return 
        id = ret[2]
        if self.user.checkDataUser(id) == mysql_query_status['USER_EXIST']:
            ls = self.user.getDataUser(id)
            self.lbDisplayName.setText(ls[infor_user['Name']])
            self.lbIDUserData.setText('ID: ' + ls[infor_user['ID']])
            self.lbDisplayAddress.setText(ls[infor_user['Address']])
            self.lbDisplayCity.setText(ls[infor_user['City']])
            self.lbDisplayCountry.setText(ls[infor_user['Country']])
            self.lbViewUser.setScaledContents(True)
            self.lbViewUser.setPixmap(QPixmap(ls[infor_user['Images']]))

            # logging data to  attendace list (using face recognition)
            csv_data_logging(ls[infor_user['Name']], ls[infor_user['ID']], ls[infor_user['Address']], ls[infor_user['City']], ls[infor_user['Country']])

        else:
            # Display the message user doesn't register yet
            msg = QMessageBox() 
            msg.setWindowTitle("information")
            msg.setText("User doesn't exits, please register!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

    def scanTagsUserData(self, timeout):
        start_time = time.time()
        while(True):
            if time.time() - start_time > timeout:
                print('Scan tags recogniton received  timeout')
                msg = QMessageBox() 
                msg.setWindowTitle("information")
                msg.setText("received timeout!!")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Ok)
                x = msg.exec_() # execute the message
                break 

            checkData, receiveData = self.ser.get_data_from_device()
            
            if checkData > 0:
                # Processing receive data
                self.dataDisplay = ''
                for i in range(len(receiveData)):
                    self.dataDisplay += '{0:x}'.format(receiveData[i])
                self.dataDisplay = str(int(self.dataDisplay, 16))
                self.lbIDUserData.setText('ID: ' + self.dataDisplay)

                id = self.lbIDUserData.text()[4: len(self.lbIDUserData.text())]
                if self.user.checkDataUser(id) == mysql_query_status['USER_EXIST']:
                    ls = self.user.getDataUser(id)
                    self.lbDisplayName.setText(ls[infor_user['Name']])
                    self.lbIDUserData.setText('ID: ' + ls[infor_user['ID']])
                    self.lbDisplayAddress.setText(ls[infor_user['Address']])
                    self.lbDisplayCity.setText(ls[infor_user['City']])
                    self.lbDisplayCountry.setText(ls[infor_user['Country']])
                    self.lbViewUser.setScaledContents(True)
                    self.lbViewUser.setPixmap(QPixmap(ls[infor_user['Images']]))
                                    
                    # logging data to  attendace list (using face recognition)
                    csv_data_logging(ls[infor_user['Name']], ls[infor_user['ID']], ls[infor_user['Address']], ls[infor_user['City']], ls[infor_user['Country']])

                else:
                    # Display the message user doesn't register yet
                    msg = QMessageBox() 
                    msg.setWindowTitle("information")
                    msg.setText("User doesn't exits, please register!!")
                    msg.setIcon(QMessageBox.Information)
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    x = msg.exec_() # execute the message
                break

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
            if self.user.mysqlConnection():
                # setting multi-media for the display 
                self.lb_select.setGeometry(-10, 460, 51, 61)
                self.groupBoxConnection.setVisible(True)
                self.groupBoxUserData.setVisible(True) 
                self.groupBoxImageID.setVisible(True)

                self.lbReadingTag.setVisible(False)  
                self.grapViewImgReadingTag.setVisible(False)
                self.btnCloseTag.setVisible(False)
                self.lbLoading.setVisible(False)

                self.radioSearchName.setChecked(True)
                # self.clearDisplayData()
                self.displayTable()

            else:
                print("error connecting to the server")
                msg = QMessageBox() 
                msg.setWindowTitle("information")
                msg.setText("Error conneting to the server, plesse check the network connection!!")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Ok)
                x = msg.exec_() # execute the message
            
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
        # self.lbReadingTag.setVisible(True)  
        # self.grapViewImgReadingTag.setVisible(True)
        # self.btnCloseTag.setVisible(True)
        # self.lbLoading.setVisible(True)

        self.receivedDataFromReader(5)

    def receivedDataFromReader(self, timeout):
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print("received timeout") 
                msg = QMessageBox() 
                msg.setWindowTitle("Information")
                msg.setText("Receive timeout!!!")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Ok)
                x = msg.exec_() # execute the message
                break

            checkData, receiveData = self.ser.get_data_from_device()

            if checkData > 0:
                # Processing receive data
                self.dataDisplay = ''
                for i in range(len(receiveData)):
                    self.dataDisplay += '{0:x}'.format(receiveData[i])

                self.dataDisplay = str(int(self.dataDisplay, 16))
                self.lbID.setText('ID    ' + self.dataDisplay)

                idRaw = self.lbID.text()
                lenIdRaw = len(idRaw)
                self.idUser = idRaw[6: lenIdRaw]

                # Disable lable loading
                self.lbReadingTag.setVisible(False)  
                self.grapViewImgReadingTag.setVisible(False)
                self.btnCloseTag.setVisible(False)
                self.lbLoading.setVisible(False)

                # Check the data exits or not 
                status = self.user.checkDataUser(self.idUser)
                if  status == mysql_query_status['USER_EXIST']:
                    # User exists
                    msg = QMessageBox() 
                    msg.setWindowTitle("Information")
                    msg.setText("User registered, do you want to edit the data ?")
                    msg.setIcon(QMessageBox.Question)
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setDefaultButton(QMessageBox.Ok)
                    x = msg.exec_() # execute the message
                    if x == QMessageBox.Ok:
                        self.displayEditUser()
                        self.flagUpdate = True

                break

    def displayEditUser(self):
        # display data user to edit
        user = self.user.getDataUser(self.idUser)
        self.textName.setPlainText(user[infor_user['Name']])  
        self.textAddress.setPlainText(user[infor_user['Address']]) 
        self.textCity.setPlainText(user[infor_user['City']]) 
        self.textCountry.setPlainText(user[infor_user['Country']]) 
        self.imagePath = user[infor_user['Images']]
        
        # display the image to button
        self.btnBrowseImage.setIconSize(self.btnBrowseImage.size())
        self.btnBrowseImage.setIcon(QtGui.QIcon(self.imagePath))

        print('Infor the user for updating: ', user)

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
        
        elif len(self.name) == 0 or len(self.address) == 0 \
            or len(self.city) == 0 or len(self.country) == 0:
            print("Not eligible for registration because the textbox yet fill out")
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please fill in the textbox completely!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

        else:
            if len(self.imagePath) == 0:
                print("Not eligible for registration because the browse choose the image yet ") 
                msg = QMessageBox() 
                msg.setWindowTitle("Information")
                msg.setText("Please click the scan browse to have the image of user!!!")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Ok)
                x = msg.exec_() # execute the message
            else:
                if not self.flagUpdate:
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
                        self.displayTable()
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText('Data failed')
                        msg.setInformativeText('Data failed to save')
                        msg.setWindowTitle("Error")
                        x = msg.exec_()
                else:
                    # check whether that changes what
                    oldUser = self.user.getDataUser(self.idUser)
                    if oldUser[0] != self.name:
                        print('updating name for the user')
                        self.user.updateUser(self.idUser, table_columns_elements[infor_user['Name']], self.name)
                    if oldUser[2] != self.address:
                        print('updating address for the user')
                        self.user.updateUser(self.idUser, table_columns_elements[infor_user['Address']], self.address)
                    if oldUser[3] != self.city:
                        print('updating city for the user')
                        self.user.updateUser(self.idUser, table_columns_elements[infor_user['City']], self.city)
                    if oldUser[4] != self.country:
                        print('updating country for the user')
                        self.user.updateUser(self.idUser, table_columns_elements[infor_user['Country']], self.country)
                    print('updating time register for the user')
                    self.user.updateUser(self.idUser, table_columns_elements[infor_user['Time']], self.timeRegister)
                    
                    # convert flagUpdate
                    self.flagUpdate = False
                    print('updating for user successfull')
                    
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

        # Choose the image file for the user data
        filename = QFileDialog.getOpenFileName()
        self.imagePath = filename[0]
        print('image path'.format(self.imagePath))
        # self.imagePath = os.path.split(imagePath)[-1]

        if self.lbID.text() == 'ID    _________':
            print("Not eligible for registration because the id user yet scan") 
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please click the scan button to have the code tags!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

        elif len(self.textName.toPlainText()) == 0 or len(self.textAddress.toPlainText()) == 0 \
            or len(self.textCity.toPlainText()) == 0 or len(self.textCountry.toPlainText()) == 0:
            print("Not eligible for registration because the textbox yet fill out")
            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Please fill in the textbox completely!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
        else:
            # get data user into the file (include image, name, id, ....)
            self.faceRecognition.facial_landmarks(self.idUser)
            self.faceRecognition.trainingUser()

            # display the image to button
            self.btnBrowseImage.setIconSize(self.btnBrowseImage.size())
            self.btnBrowseImage.setIcon(QtGui.QIcon(self.imagePath))

            msg = QMessageBox() 
            msg.setWindowTitle("Information")
            msg.setText("Get imgae uset successfully!!!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)

    def displayTable(self):
        self.updateNumberUser()
        users = []
        users = self.user.getAllUser()

        # Creating  empty table
        self.tableWidget.setRowCount(self.numUserRegister)  
        self.tableWidget.setColumnCount(6)   

        # Display label for the table
        self.tableWidget.setHorizontalHeaderLabels(('Name', 'ID', 'Address', 'City', 'Country', 'Time'))

        # Table will fit the screen horizontally 
        self.tableWidget.horizontalHeader().setStretchLastSection(True) 
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        

        row = 0
        # Display elements in User
        for user in users:
            column = 0
            for i in range (len(user) - 1):
                item = QTableWidgetItem(user[i])

                # make cell not editable
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row, column, item)
                column += 1
            row += 1     
                 
        # self.tableWidget.sortByColumn(0, QtCore.Qt.AscendingOrder) 
        
        # Adjust size of Table
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        
        # Add Table to Grid
        grid = QGridLayout()
        grid.addWidget(self.tableWidget, 0, 0)

        # add event when the mouse is click by the admin
        self.tableWidget.viewport().installEventFilter(self)

        # selecting default the row just to init
        if self.tableWidget.rowCount() > 0:
            self.tableWidget.selectRow(0)
            self.displayImageRegister(0)
            
    def updateNumberUser(self):
        # loading  the number of user on database
        self.numUserRegister = self.user.getNumberUser()

    def eventFilter(self, source, event):
        if self.tableWidget.selectedIndexes() != []:
            row = self.tableWidget.currentRow()
            col = self.tableWidget.currentColumn()
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if event.button() == QtCore.Qt.LeftButton:
                        row = self.tableWidget.currentRow()
                        col = self.tableWidget.currentColumn()
                        self.tableWidget.selectRow(row)
                        print('Left mouse:({}, {}) was pressed'.format(row, col))

                        # display image the registerd user
                        self.displayImageRegister(row)
                    elif event.button() == QtCore.Qt.RightButton:

                        row = self.tableWidget.currentRow()
                        col = self.tableWidget.currentColumn()
                        print('Right mouse: ({}, {}) was pressed'.format(row, col))

                        # Creatin list widget
                        self.creatingListWidget()
            
        return QtCore.QObject.event(source, event)

    def displayImageRegister(self, row):
        id = self.tableWidget.item(row, 1).text()
        dateRegister = self.tableWidget.item(row, 5).text()
        print('id: {}, date: {} has been taken from table'.format(id, dateRegister))
        self.lbViewRegister.setScaledContents(True)
        self.lbViewRegister.setPixmap(QPixmap('picture/image_save/{}_{}.jpg'.format(id, dateRegister)))

    def creatingListWidget(self):
       pass
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