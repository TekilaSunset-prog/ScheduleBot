import sqlite3

connection = sqlite3.connect('schedule')
cursor = connection.cursor()

cursor.execute('SELECT * FROM Schedule')
res = cursor.fetchmany(1)
print(res)

connection.commit()
connection.close()