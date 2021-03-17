import os
import sys
import csv
import datetime
import time
import pyttsx3
import sqlite3
import mysql.connector
import yagmail

path = 'Attendance'


#===============================================================================
# process and speak message
#===============================================================================
def speakMessage(message, rate, volume, voices):
        engine = pyttsx3.init()
        # RATE
        _rate = engine.getProperty('rate')                 # getting details of current speaking rate
        print ("Rate has been setted: {}".format(_rate))  
        engine.setProperty('rate', rate)                       # setting up new voice rate

        # VOLUME 
        _volume = engine.getProperty('volume')             # getting to know current volume level (min = 0 and max = 1)
        print ("Volume has been setted: {}".format(_volume))    # printing current volume level
        engine.setProperty('volume', volume)                   # setting up volume level  between 0 and 1

        # VOICES     
        _voices = engine.getProperty('voices')             # getting details of current voice    
        if voices == 0:
            print ("Voices has been setted: {}".format("male")) 
            self.engine.setProperty('voice', _voices[0].id)     # changing index, changes voices. o for male
        else:
            print ("Voices has been setted: {}".format("female")) 
            engine.setProperty('voice', _voices[1].id)     # changing index, changes voices. 1 for female

        engine.say('{}'.format(message))
        engine.runAndWait()

#===============================================================================
# Log debug
#===============================================================================
def PRINT_INFO_LOG(message):
    print('[INFO] ' + message)

def PRINT_ERROR_LOG(message):
    print('[ERROR] ' + message)



#===============================================================================
# Fet current time
#===============================================================================
def get_current_time():
    now = datetime.datetime.now()
    time_now = now.strftime("%m_%d_%Y_%H_%M_%S")
    return time_now



#===============================================================================
# creating the title bar function
#===============================================================================
def title_bar(): 
    os.system('cls') # for windows

    # Title of the program
    print("\t**********************************************")
    print("\t***** Face And Tags Recognition Attendance System *****")
    print("\t**********************************************")


#===============================================================================
# logging data to csv file
#===============================================================================
def csv_data_logging(name, id, address, city, country):
    ts = time.time()
    date_attendance = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    time_attendance = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')


    file_name = 'Attendance' + os.sep + 'Attendance_' + date_attendance + '.csv'
    file_exists = os.path.isfile(file_name)

    fieldnames = ['Name', 'ID', 'Address', 'City', 'Country', 'Date', 'Time']


    with open(file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            print('File test report {} has been created !!!'.format(file_name))
        writer.writerow({'Name': name, 'ID': id, 'Address': address, 
                    'City': city, 'Country': country, 'Date': date_attendance, 'Time': time_attendance})
        print('User has been added to the attendance list ')
                        
    
#===============================================================================
# Send email address to admin
#===============================================================================
def sendEmailToAdmin():
    date = datetime.date.today().strftime("%B %d, %Y")

    # receiver email address
    receiver = 'quoc.bui1999@hcmut.edu.vn'

    # Change the current working directory to the specified path.
    os.chdir(path)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    print(files)
    if len(files) == 0:
        print('Not exitst file in the attendance folder')
        return

    newest = files[-1]
    filename = newest
    sub = "Attendance Report for " + str(date)

    # mail information
    yag = yagmail.SMTP("quocquocbui1999@gmail.com", "buivanquoc")

    # sent the mail
    yag.send(
        to = receiver,
        subject = sub, # email subject
        contents = 'Attendance File',  # email body
        attachments = filename  # file attached
    )
    print('{} file sent to admin!'.format(filename))