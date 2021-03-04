
import sys
import os
from serial_attendance import *
import mysql.connector
from mysql.connector import errorcode


TABLE_NAME = 'user_data_table'
DATABASE_NAME = 'attendance_system_data'

table_columns_elements = {
    0 : 'Name',
    1 : 'ID',
    2 : 'Address',
    3 : 'City',
    4 : 'Country',
    5 : 'Images',
}


dictConnect = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : '',
    'database' : DATABASE_NAME,
    'port' : 3307,    
}

mysql_query_status = {
    'CONNECTION_OK': 1,
    'CONNECTION_ERROR': 2,
    'INSET_OK': 3
}



class UserInfor:
    # Temporary hard code totalUser = 0
    totalUser =  0
    def __init__(self):
        self.name = ''
        self.idUser = ''
        self.address = ''
        self.city = ''
        self.country = ''
        self.imagePath = ''

        self.myDatabase = ''
        self.myCursor = ''

        # TODO: Loading data and count how many users  were registerd  

    def saveData(self, name, address, city, country, imagePath, idUser):
        self.name = name
        self.address = address
        self.city = city
        self.country = country
        self.imagePath = imagePath
        self.idUser = idUser

        #TODO: Add the data to database

    # Check data from database
    def checkDataFromDataBase(self):
        # Temporary hardcode not exits the user
        return False

    def mysqlConnection(self):
        ret = False
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            ret = True
            print('Connecting successfully')

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
                print('Something error')
        finally:
            return ret
    
    def mysqlDisconnect(self):
        try:
            self.myDatabase.close()
            print('Disconnecting successfully')
        except:
            print('Fail to disconnect the database')

    def insertData(self, name, idUser, address, city, country, imagePath):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')
            insertQueryColumns = "INSERT INTO {} ({}, {}, {}, {}, {}, {}) ".format(TABLE_NAME, 
                                                                    table_columns_elements[0], 
                                                                    table_columns_elements[1], 
                                                                    table_columns_elements[2], 
                                                                    table_columns_elements[3], 
                                                                    table_columns_elements[4], 
                                                                    table_columns_elements[5]) + \
                                                                    "VALUES (%s, %s, %s, %s, %s, %s)"

            self.name = name
            self.idUser = idUser 
            self.address = address
            self.city = city
            self.country = country
            self.imagePath = self.convertToBinaryData(imagePath)

            # Convert data into tuple format
            insertQueryValues = (self.name, self.idUser, self.address, self.city, self.country, self.imagePath)                                                                                 
            self.myCursor.execute(insertQueryColumns, insertQueryValues) 

            insertQueryValues = (self.name, self.idUser, self.address, self.city, self.country, os.path.split(imagePath)[-1])  
            print('Table {} inserted successfully'.format(insertQueryColumns) % (insertQueryValues))  
            print(self.myCursor.rowcount, 'details inserted')

            # To ensure the data insertion, Always commit to the database.
            self.myDatabase.commit()  

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Error: Something is wrong with your user name or password')
                return mysql_query_status['CONNECTION_ERROR']

            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Error: Database does not exist')
                return mysql_query_status['CONNECTION_ERROR']
            elif err.errno == errorcode.ER_DUP_ENTRY:
                print('Error: Database was duplicated')
                return mysql_query_status['CONNECTION_ERROR']
            else:
                print('Error: Failed to inserting data into MYSQL table {}').format(err)
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')

    def writeFile(self, data, filename):
        # Convert binary data to proper format and write it on Hard Disk
        with open('{}.png'.format(filename), 'wb') as file:
            file.write(data)
        file.close()

    def selectTable(self):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')

            query = 'SELECT * FROM {}'.format(TABLE_NAME)
            self.myCursor.execute(query)
            record = self.myCursor.fetchall()
            for row in record: 
                print('{} = {}'.format(table_columns_elements[0], row[0]))
                print('{} = {}'.format(table_columns_elements[1], row[1]))
                print('{} = {}'.format(table_columns_elements[2], row[2]))
                print('{} = {}'.format(table_columns_elements[3], row[3]))
                print('{} = {}'.format(table_columns_elements[4], row[4]))
                print('Storing employee image and bio-data on disk')
                #TODO: save the image adhere to format included both name and id  
                self.writeFile(row[5], 'photo')
                break

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Error: Something is wrong with your user name or password')
                return mysql_query_status['CONNECTION_ERROR']

            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Error: Database does not exist')
                return mysql_query_status['CONNECTION_ERROR']
            elif err.errno == errorcode.ER_DUP_ENTRY:
                print('Error: Database was duplicated')
                return mysql_query_status['CONNECTION_ERROR']
            else:
                print('Error: Failed to read the data from MYSQL table {}').format(err)
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')

    def sortTable(self):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')

            query = 'SELECT * FROM {}'.format(TABLE_NAME)
            self.myCursor.execute(query)
            record = self.myCursor.fetchall()
            for row in record: 
                print('{} = {}'.format(table_columns_elements[0], row[0]))
                print('{} = {}'.format(table_columns_elements[1], row[1]))
                print('{} = {}'.format(table_columns_elements[2], row[2]))
                print('{} = {}'.format(table_columns_elements[3], row[3]))
                print('{} = {}'.format(table_columns_elements[4], row[4]))
                print('Storing employee image and bio-data on disk')
                #TODO: save the image adhere to format included both name and id  
                self.writeFile(row[5], 'photo')
                break

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print('Error: Something is wrong with your user name or password')
                return mysql_query_status['CONNECTION_ERROR']

            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Error: Database does not exist')
                return mysql_query_status['CONNECTION_ERROR']
            elif err.errno == errorcode.ER_DUP_ENTRY:
                print('Error: Database was duplicated')
                return mysql_query_status['CONNECTION_ERROR']
            else:
                print('Error: Failed to read the data from MYSQL table {}').format(err)
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')




    def deleteTable(self):
        pass


    def convertToBinaryData(self, filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData

    
    
        

    
        
    
    


    

    