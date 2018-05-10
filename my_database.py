from flask_mysqldb import MySQL
from flask import Flask
from app import mysql

def update(statement, varriables):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute(statement, varriables)

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

def queryOne(statement, varriables):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    results = cur.execute(statement, varriables)
    
    result = cur.fetchone()
    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    return result

def queryAll(statement, varriables):
    # Create cursor
    cur = mysql.connection.cursor()
    if varriables == "":
        # Execute
        results = cur.execute(statement)
    else:
        # Execute
        results = cur.execute(statement, varriables)
    result = cur.fetchall()
    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    return result