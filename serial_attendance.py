import serial
import time 
from smart_util import *
from PyQt5.QtWidgets import QMessageBox


# frame stuctures
RFID_FRAME_HEADER_SIZE = 4
RFID_FRAME_FOOTER_SIZE = 4
RFID_FRAME_DATA_SIZE = 5
RFID_FRAME_FOOTER_VALUE= ord('$')

# responses 
RFID_PING_MSG_ID = 0x28
RFID_REQ_MSG_ID = 0x21
RFID_ACK_MSG_ID = 0xC1
RFID_NACK_MSG_ID = 0xC2

# Command control device
rfid_command_id = {
    'RFID_CMD_OPEN_DOOR'    : 1,
    'RFID_CMD_CLOSE_DOOR'   : 2,
}

# header
RDID_HEADER: str = "RFIC"
PING_HEADER: str = "RFIP"
RESPONSE_HEADER: str = "RFIR"
ACK_HEADER: str = "AACK"
NACK_HEADER: str = "NACK"
FOOTER: str = "$$$$"

headerFrame = {'NO_RFID_HEADER': 0,
               'RFID_RESPONSE': 1, 
               'RFID_ACK': 2, 
               'RFID_NACK': 3}


rx_msg_status = {
    'OK': 1,
    'INVALID': 2,
    'TIME_OUT': 3
}

SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 19200


class SerialComm:
    def __init__(self):
        self._payLoad = 0
        self._header = []
        self._footer = []
        self.tx_message = []
        self.receiveParams = []
        self.sendParams = []
        self.isIgnoreData = False


        # variable for receive function
        self.rfid_header = headerFrame['NO_RFID_HEADER']
        self.num_received_footer_bytes = 0
        self.received_idx = 0

        self.receive_data = b'' # Serial is bytes data
        self.rfid_header = headerFrame['NO_RFID_HEADER']
        self.return_data = b''

    def connectSerial(self):
        # Init the serial port
        self.ser = serial.Serial(port= SERIAL_PORT,
                                baudrate=BAUDRATE,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS, timeout = 0)
                                
        # clear buffer input and output                      
<<<<<<< HEAD
        self.ser.flushOutput()
        self.ser.flushInput()
        print('Connected {} with Baudrate: {}'.format(serialPort, baudRate))
=======
        self.emptyBufferSerial(True)
        self.emptyBufferSerial(False)
        print('Connected {} with Baudrate: {}'.format(SERIAL_PORT, BAUDRATE))
>>>>>>> Attendance_System/Face_Recognize
    
    
    def closeSerial(self):
        self.ser.close()

    def emptyBufferSerial(self, input):
        if input == True:
            self.ser.flushInput()
        else:
            self.ser.flushOutput()

    # def getPortNumber(self):
    #     result = []
    #     ports = serial.tools.list_ports_windows.comports(include_links=False)
    #     # list port names
    #     for port in ports :
    #         result.append(port.device)
            
    #     return result

    # ******************************************************************************************************************
    # Receive Async Data    
    # ******************************************************************************************************************

    def get_data_from_device(self):
        ret = 0
        # receive data from serial port
        if self.isIgnoreData:
            while self.ser.inWaiting() > 0:
                self.ser.read()
            self.isIgnoreData = False

        if not self.isIgnoreData:
            if self.ser.inWaiting():
                self.received_idx += 1
                self.receive_data += self.ser.read()
                print('inWaiting: {}'.format(self.ser.inWaiting()))
                
                if self.rfid_header == headerFrame['NO_RFID_HEADER']:
                    # Validate header frame
                    if self.received_idx == RFID_FRAME_HEADER_SIZE:
                        if self.receive_data == b'RFIR':
                            self.rfid_header = headerFrame['RFID_RESPONSE']
                        elif self.receive_data == b'AACK':
                            self.rfid_header = headerFrame['RFID_ACK']
                        elif self.receive_data == b'NACK':
                            self.rfid_header = headerFrame['RFID_NACK']   
                        else:   
                            self.rfid_header = headerFrame['NO_RFID_HEADER']                
                            self.received_idx -= 1
                            self.receive_data = self.receive_data[1:RFID_FRAME_HEADER_SIZE]    

                if self.rfid_header == headerFrame['RFID_RESPONSE']:
                    # TODO: get payload lenght
                    frame_size = RFID_FRAME_HEADER_SIZE + RFID_FRAME_DATA_SIZE + RFID_FRAME_FOOTER_SIZE
                                                            
                    # Keep receive data until reach end of frame
                    if self.received_idx == frame_size:
                        # Validate footer frame
                        if self.receive_data[(self.received_idx - RFID_FRAME_FOOTER_SIZE): self.received_idx] == b'$$$$':
                            print("Received: ", self.receive_data)
                            ret = len(self.receive_data)
                            self.return_data = self.receive_data[RFID_FRAME_HEADER_SIZE: ret - RFID_FRAME_FOOTER_SIZE]

                        self.rfid_header = headerFrame['NO_RFID_HEADER']
                        self.receive_data = b''
                        self.received_idx = 0
                        self.isIgnoreData = True
                    
            return ret, self.return_data       

    # ******************************************************************************************************************
    # Send Async Data    
    # ******************************************************************************************************************
    def pc_send_data_to_device(self, msg_id, msg_data = None):
        """
        Send a request to the device 
        return: none
        """
        # Initial for sendRequest
        if msg_data is None:
            msg_data = []
        self.tx_message.clear()
        
        # Check message ID
        if msg_id == RFID_REQ_MSG_ID:
            self._header = RDID_HEADER
        elif msg_id == RFID_PING_MSG_ID:
            self._header = PING_HEADER
        elif msg_id == RFID_ACK_MSG_ID:
            self._header = ACK_HEADER
        elif msg_id == RFID_NACK_MSG_ID:
            self._header = NACK_HEADER

        self._footer = FOOTER
        self.sendParams = msg_data

        # packing transmisstion frame  
        self.tx_message.extend(self._header.encode())
        self._payLoad = len(msg_data)
        self.tx_message.extend(self._payLoad.to_bytes(2, byteorder='big')) 
<<<<<<< HEAD
        self.tx_message.extend(msg_data) 
=======
        # self.tx_message.extend(msg_data.encode()) 
>>>>>>> Attendance_System/Face_Recognize
        self.tx_message.extend(self._footer.encode())   

        # send data to device
        self.ser.flushOutput()
        self.ser.write(self.tx_message)
        print("Send cmd:", bytearray(self.tx_message))