import mysql.connector



dictConnect = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : '',
    'database' : 'learning_mysql',
    'port' : 3307,
}


try:
    conn = mysql.connector.connect(**dictConnect)
    print(conn)

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)



myCursor = conn.cursor()
myCursor.execute('INSERT INTO names (id, name')

# class MySqlConnect():
#     def __init__(self):
#         self.__init__()
# 

conn.commit() 
conn.close()