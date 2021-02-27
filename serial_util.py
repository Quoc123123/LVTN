from serial_attendance import *



class SerialUtil:
    def __init__(self):
        super().__init__()
        self.ser = SerialComm()
        self.msg_data = []
        self.response_data = b''

    def send_ack_message(self): 
        self.ser.pc_send_data_to_device(RFID_ACK_MSG_ID)

    def send_nack_message(self): 
        self.ser.pc_send_data_to_device(RFID_NACK_MSG_ID)

    def send_ping_message(self, timeout): 
        self.ser.pc_send_data_to_device(RFID_PING_MSG_ID) 
        # wait for ACK/NACK response
        receive_msg = self.pc_get_data_from_device(timeout)
        if receive_msg.decode() == (ACK_HEADER + FOOTER):
            print('Ping Successfully')
            return rx_msg_status['OK']
        elif receive_msg.decode() == (NACK_HEADER + FOOTER):
            print('Ping FAILED')
            return rx_msg_status['INVALID']
        else:
            print('Ping Time Out')
            return rx_msg_status['TIME_OUT']

    def request_message(self):
        self.ser.pc_send_data_to_device(RFID_PING_MSG_ID, msg_data)

    def receive_message(self):
        pass
    

    
