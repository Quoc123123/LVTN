import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.uic import loadUi
import pyrebase
from smart_util import *
from serial_attendance import *


listPort = []


 
firebaseConfig = {   
    'apiKey': "AIzaSyAx3uJ5dHV8jtxAENTPEbt7mh_hokOhMbY",
    'authDomain': "authdemo-53b68.firebaseapp.com",
    'databaseURL': "https://authdemo-53b68.firebaseio.com",
    'projectId': "authdemo-53b68",
    'storageBucket': "authdemo-53b68.appspot.com",
    'messagingSenderId': "682934666195",
    'appId': "1:682934666195:web:82722e1846c8dc32126526",
    'measurementId': "G-V9QMHWTF6K"
    }

firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()  


class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("design_ui/login.ui", self)
        self.btn_login.clicked.connect(self.loginFunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)   # not display password
        self.btn_createAccount.clicked.connect(self.gotoCreate)
        self.lb_status.setVisible(False)

    def loginFunction(self):
        email=self.email.text()
        password=self.password.text()
        
        # try:
        #     auth.sign_in_with_email_and_password(email, password)
        #     self.lb_status.setVisible(False)
        #     loginMessage = '''Welcome Admin. You can Add Student or Delete Student or View Existing Student
        #                       Enter Com port and Baud Rate and press scan RFID  Button to assign a Tag
        #                    '''
        #     speakMessage(loginMessage, 125, 1, 1)
        # except:
        #     self.lb_status.setVisible(True)
        #     loginMessage = 'Invalid Credentials please try again '
        #     speakMessage(loginMessage, 125, 1, 1)

        pageOne = PageOne()
        widget.addWidget(pageOne)
        widget.setFixedWidth(700)
        widget.setFixedHeight(750)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoCreate(self):
        createacc = CreateAcc()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class CreateAcc(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("design_ui/createacc.ui", self)
        self.btn_signup.clicked.connect(self.createAccFunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lb_status.setVisible(False)

    def createAccFunction(self):
        email = self.email.text()
        if self.password.text() == self.confirmpass.text():
            password = self.password.text()
            # print("Successfully created acc with email: ", email, "and pass ", password)
            try:
                auth.create_user_with_email_and_password(email, password) 
                # setting the screens to mainwindow
                login = Login()
                widget.addWidget(login)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            except:
                # print("Invalid email")
                self.lb_status.setVisible(True)

# ******************************************************************************************************************
# PageOne of UI  
# ******************************************************************************************************************
class PageOne(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("design_ui/page_one.ui", self)
        # setting for connecting
        self.btnScanRfid.setEnabled(False)
        self.btnAttendance.setEnabled(False)    
        self.flagConnect = False
        self.addComPort()
        
        # connect to envent of button
        self.btnScanRfid.clicked.connect(self.scan)
        self.btnAddUser.clicked.connect(self.addDatabase)
        self.btnDeleteUser.clicked.connect(self.deleteUser)
        self.btnShowUser.clicked.connect(self.showUser)
        self.btnConnect.clicked.connect(self.connectComPort)
        self.btnBackToHome.clicked.connect(self.backToHome)
        self.btnAttendance.clicked.connect(self.attendance)
        self.btnClearText.clicked.connect(self.clearText)
        
    # add listport into ComboBox
    def addComPort(self):
        self.ser = SerialComm()
        listPort = self.ser.getPortNumber()
        # print(listPort)
        for port in listPort:
            self.cbxComPort.addItem(port)

    # connect to port from Combobox
    def connectComPort(self):
        if self.flagConnect == False:
            self.btnConnect.setText('Disconnect')
            self.flagConnect = True
            comPort = self.cbxComPort.currentText()
            # print(comPort)
            self.btnScanRfid.setEnabled(True)
            self.btnAttendance.setEnabled(True)
            # TODO: connecting to device
        else:
            self.btnConnect.setText('Connect')
            self.flagConnect = False
            self.btnScanRfid.setEnabled(False)
            self.btnAttendance.setEnabled(False)
            # TODO: Disconnecting the device

    # add uset into database
    def addDatabase(self):
        try:
            #--------------------------
            # get full name 
            firstName = self.leFirstName.text()
            midName = self.leMidName.text()
            lastName = self.leLastName.text()
 
            # get Email, Phone Number, ID (Student card/ Staff card) 
            email = self.leEmail.text()
            phoneNumber = self.lePhoneNumber.text()     
            ID = self.leId.text()
     
            # get Gender, tags ID
            gender = self.leGender.text()
            tags = self.leEnterRfid.text()
            
            # check whether completely fulfills the data yes or no
            if (len(firstName) and len(midName) and len(lastName) and len(email) \
                and len(phoneNumber) and len(ID) and len(gender) and len(tags)) >= 1:
                # display the message to user (admin)
                msg = QMessageBox() 
                msg.setWindowTitle("Add User")
                msg.setText("Do you want to add this user to the database or not?")
                msg.setIcon(QMessageBox.Question)
                msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Cancel)
                x = msg.exec_() # execute the message
                # TODO add data into database
                
            else:
                msg = QMessageBox() 
                msg.setWindowTitle("Add User")
                msg.setText("Please complete the above information!!!")
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Ok)
                x = msg.exec_() # execute the message
            
        except:
            print("CANNOT ADD TO DATABASE")
            msg = QMessageBox()
            msg.setWindowTitle("Add User") 
            msg.setText("Cannot add to database")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

    # show all of user on database
    def showUser(self):
        try:
            # TODO: Connect the database to show all of users 
            pass
        except:
            print('Could not read from database')
            msg = QMessageBox()
            msg.setWindowTitle("Show User") 
            msg.setText("Could not read from database")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
        
    # delete user from database
    def deleteUser(self):
        try:
            firstName = self.leFirstName.text()
            ID = self.leId.text()
            tags = self.leEnterRfid.text()

            # validate the data before executing delete
            if len(firstName) >= 2:
                # display the message to user (admin)
                msg = QMessageBox() 
                msg.setWindowTitle("Delete User")
                msg.setText("Do you want to delete this user to the database or not?")
                msg.setIcon(QMessageBox.Question)
                msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Cancel)
                x = msg.exec_() # execute the message
                # TODO delete the data in database
            else:
                print('QuocBrave')
                msg = QMessageBox() 
                msg.setWindowTitle("Delete User")
                msg.setText("Please complete the information including first name, id and rfid tags!!!")
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setDefaultButton(QMessageBox.Ok)
                x = msg.exec_() # execute the message
        except:
            print("CANNOT DELETE TO DATABASE")
            msg = QMessageBox()
            msg.setWindowTitle("Delete User") 
            msg.setText("Cannot delete this user from database")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message

    # scan the rfid tags from device
    def scan(self):
        try:
            # check the status whether connected or not
            # TODO: list all port on laptop/computer and connect             
            pass
        except:
            print('Could scan rfid card')
            msg = QMessageBox()
            msg.setWindowTitle("Show User") 
            msg.setText("Could scan rfid card")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            x = msg.exec_() # execute the message
    
    # Back to login UI
    def backToHome(self):
        login = Login()
        widget.addWidget(login)
        widget.setFixedWidth(480)
        widget.setFixedHeight(620)
        widget.setCurrentIndex(widget.currentIndex() + 1)


    # Enter Attendance UI
    def attendance(self):
        pageTwo = PageTwo()
        widget.addWidget(pageTwo)
        widget.setFixedWidth(700)
        widget.setFixedHeight(750)
        widget.setCurrentIndex(widget.currentIndex() + 1)
      
    # back to login UI
    def clearText(self):
        pass


# ******************************************************************************************************************
# PageTwo of UI  
# ******************************************************************************************************************
class PageTwo(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("design_ui/page_two.ui", self)
        self.btnBack.clicked.connect(self.backToPageOne)
        self.btnViewRecord.clicked.connect(self.viewRecord)

    # Back to page one
    def backToPageOne(self):
        pageOne= PageOne()
        widget.addWidget(pageOne)
        widget.setFixedWidth(700)
        widget.setFixedHeight(750)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    #  Go to page three
    def viewRecord(self):
        pageThree= PageThree()
        widget.addWidget(pageThree)
        widget.setFixedWidth(700)
        widget.setFixedHeight(750)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# ******************************************************************************************************************
# PageThree of UI  
# ******************************************************************************************************************
class PageThree(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("design_ui/page_three.ui", self)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = Login()
    widget = QtWidgets.QStackedWidget() # to switch the sceens in the case you have many windows 
    widget.addWidget(mainwindow)
    widget.setFixedWidth(480)
    widget.setFixedHeight(620)
    widget.show()
    sys.exit(app.exec_())
