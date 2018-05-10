from flask_mysqldb import MySQL
import my_database
def getID(username):
    user = my_database.queryOne("SELECT id FROM users WHERE username = %s", [username])
    id = user['id']
    return id

def getByUsername(username):
    user = my_database.queryOne("SELECT * FROM users WHERE username = %s", [username])
    return user

def getAllUsers():
    user = my_database.queryAll("SELECT * FROM users","")
    return user

def getByFirstName(firstname):
    user = my_database.queryAll("SELECT * FROM users WHERE first_name LIKE %s",('%' + firstname + '%',))
    return user

def getByLastName(lastname):
    user = my_database.queryAll("SELECT * FROM users WHERE last_name LIKE %s", ('%' + lastname + '%',))
    return user

def getByBothName(bothname):
    first = bothname[0]
    last = bothname[1]
    user = my_database.queryAll("SELECT * FROM users WHERE first_name LIKE %s and last_name LIKE %s", ('%' + first + '%', '%' + last + '%'))
    return user

def updateProfile (password, first_name, last_name, DOB, gender, email, username):
    statement = "UPDATE users SET password=%s, first_name=%s, last_name=%s, DOB=%s, gender=%s, email=%s WHERE username=%s "
    my_database.update(statement,(password, first_name, last_name, DOB, gender, email, username))

def updatePhoto(photo, username):
    statement = "UPDATE users SET photo=%s WHERE username=%s "
    my_database.update(statement,(photo, username))

def createUser(username, password, first_name, last_name, DOB, gender, email, photo):
    statement = "INSERT INTO users(username, password, first_name, last_name, DOB, gender, email, photo) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"    
    my_database.update(statement, (username, password, first_name, last_name, DOB, gender, email, photo))
