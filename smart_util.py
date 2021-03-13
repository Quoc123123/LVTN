import os
import sys
import csv
import datetime
import time
import pyttsx3
import sqlite3
import mysql.connector



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
