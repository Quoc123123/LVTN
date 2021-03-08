
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
    5 : 'Time',
    6 : 'Images',
}


dictConnect = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : '',
    'database' : DATABASE_NAME,
    'port' : 3307,    
}

mysql_query_status = {
    'OK': 0,
    'ERROR': 1,
    'CONNECTION_ERROR': 2,
    'INSET_OK': 3,
    'INSET_ERROR': 4,
    'UPDATE_OK': 5,
    'UPDATE_ERROR': 6,
    'DELETE_OK': 7,
    'DELETE_ERROR': 8,
    'USER_EXIST': 9,
    'USER_NOT_EXIST': 10,
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
        self.timeRegister = ''
        self.imagePath = ''

        self.myDatabase = ''
        self.myCursor = ''

        # TODO: Loading data and count how many users  were registerd  

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
            self.myCursor.close()
            self.myDatabase.close()
            print('Disconnecting successfully')
        except:
            print('Fail to disconnect the database')

    def insertData(self, name, idUser, address, city, country, time, imagePath):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')
            insertQueryColumns = "INSERT INTO {} ({}, {}, {}, {}, {}, {}, {}) ".format(TABLE_NAME, 
                                                                    table_columns_elements[0], 
                                                                    table_columns_elements[1], 
                                                                    table_columns_elements[2], 
                                                                    table_columns_elements[3], 
                                                                    table_columns_elements[4], 
                                                                    table_columns_elements[5],
                                                                    table_columns_elements[6]) + \
                                                                    "VALUES (%s, %s, %s, %s, %s, %s, %s)"

            self.name = name
            self.idUser = idUser 
            self.address = address
            self.city = city
            self.country = country
            self.timeRegister = time
            self.imagePath = self.convertToBinaryData(imagePath)

            # Convert data into tuple format
            insertQueryValues = (self.name, self.idUser, self.address, self.city, self.country, self.timeRegister, self.imagePath)                                                                                 
            self.myCursor.execute(insertQueryColumns, insertQueryValues) 

            insertQueryValues = (self.name, self.idUser, self.address, self.city, self.country, self.timeRegister, os.path.split(imagePath)[-1])  
            print('Table {} inserted successfully'.format(insertQueryColumns) % (insertQueryValues))  
            print(self.myCursor.rowcount, 'details inserted')

            # To ensure the data insertion, Always commit to the database.
            self.myDatabase.commit()
            return mysql_query_status['INSET_OK']

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
                print('{} = {}'.format(table_columns_elements[4], row[5]))
                print('Storing employee image and bio-data on disk')
                #TODO: save the image adhere to format included both name and id  
                self.writeFile(row[6], 'photo')
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

    def sortTable(self, columns, ascending = True):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')

            if ascending:
                query = 'SELECT * FROM {} ORDER BY {} {}'.format(TABLE_NAME, columns, 'ASC')
            else:
                query = 'SELECT * FROM {} ORDER BY {} {}'.format(TABLE_NAME, columns, 'DESC') 
            print('qerry: ' + query)
            self.myCursor.execute(query)

            record = self.myCursor.fetchall()
            for row in record: 
                print(row[:-1])

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
                print('Error: Failed to ascending the data from MYSQL table {}').format(err)
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')

    def deleteRow(self, id):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')

            query = 'DELETE FROM {} WHERE {} = {}'.format(TABLE_NAME, table_columns_elements[1], id)
            print('query: ' + query)
            self.myCursor.execute(query)
            
            # To ensure the data insertion, Always commit to the database.
            self.myDatabase.commit()  
            print('number of rows deleted', self.myCursor.rowcount)


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
                print('Error: Failed to delete record from MYSQL table {}').format(err)
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')

    def updateUser(self, id, columns, value):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')
            print('Before updating a record')
            query = 'SELECT *  FROM {} WHERE {} = {}'.format(TABLE_NAME, table_columns_elements[1], id)
            print('query: ' + query)
            self.myCursor.execute(query)
            record = self.myCursor.fetchone()
            print(record)

            # Update single record now
            query = "UPDATE {} SET {} = '{}' WHERE {} = {}".format(TABLE_NAME, columns, value, table_columns_elements[1], id)
            print('query: ' + query)
            
            self.myCursor.execute(query)
            # To ensure the data insertion, Always commit to the database.
            self.myDatabase.commit()  
            print('Record updated successfully')
            print('After updating record')
            query = 'SELECT *  FROM {} WHERE {} = {}'.format(TABLE_NAME, table_columns_elements[1], id)
            self.myCursor.execute(query)
            record = self.myCursor.fetchone()
            print(record)

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
                # Update failed message as an error
                print('Error: Failed to update record from MYSQL table {}').format(err)
                # reverting changes because of exception
                self.myCursor.rollback()
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')

    def getNumberUser(self):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')

            # get number rows in a table and give your table
            query = 'SELECT *  FROM {}'.format(TABLE_NAME)
            number_of_rows = self.myCursor.execute(query)
            print(number_of_rows)
            return number_of_rows

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
                print('Error: Failed to ascending the data from MYSQL table {}').format(err)
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')

    def checkDataUser(self, ID):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')
            
            query = 'SELECT * FROM {}'.format(TABLE_NAME)
            self.myCursor.execute(query)
            record = self.myCursor.fetchall()
            for row in record: 
                # print('{} = {}'.format(table_columns_elements[1], row[1]))
                if ID == row[1]:
                    print('exist data user: {}'.format(row[:-1]))
                    self.mysqlDisconnect()
                    return mysql_query_status['USER_EXIST']
            print('User register yet')
            self.mysqlDisconnect()
            return mysql_query_status['USER_NOT_EXIST']    
                
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
                print('Error: Failed to ascending the data from MYSQL table {}').format(err)
                return mysql_query_status['CONNECTION_ERROR']
        finally:
           if self.myDatabase.is_connected():
                self.myCursor.close()
                self.myDatabase.close()
                print('MySQL connection is closed')
        
        
    def getDataUser(self, ID):
        try:
            self.myDatabase = mysql.connector.connect(**dictConnect)
            print(self.myDatabase)
            self.myCursor = self.myDatabase.cursor()
            print('Connecting successfully')
            
            query = 'SELECT * FROM {}'.format(TABLE_NAME)
            self.myCursor.execute(query)
            record = self.myCursor.fetchall()
            for row in record: 
                # print('{} = {}'.format(table_columns_elements[1], row[1]))
                if ID == row[1]:
                    print('exist data user: {}'.format(row[:-1]))
                    self.mysqlDisconnect()
                    ls = list(row[:-1])
                    file_image = 'picture/image_save/{}_{}_{}'.format(ls[0], ls[1], ls[5])
                    self.writeFile(row[6], file_image)
                    ls.append(file_image)
                    print(ls)
                    return ls
                    
                
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
                print('Error: Failed to ascending the data from MYSQL table {}').format(err)
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

    def convertToBinaryData(self, filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData


    

    