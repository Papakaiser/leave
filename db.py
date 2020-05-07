import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from flask import g



def insert(app, query):
    print(query)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    cursor.close()
    connection.close()

def get_one(app, query):
    print(query)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result


def get_many(app, query):
    print(query)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def call_proc(app, query):
    print(query)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor()
    cursor.callproc(query)
    cursor.close()
    connection.close()