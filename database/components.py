import sqlite3
from sqlite3 import Error
import sys


def create_connection(db_file):
    """
    Create a database connection to the sqlite database specified by db_file
    :param db_file: database file
    :return: connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print (e)
    
    return conn


def create_table(conn, create_table_sql):
    """
    Create a table from the create_table_sql statement
    :param conn: connection object
    :param create_table_sql: a CREATE TABLE statement
    :return: None
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print (e)


def insert_data(conn, sql_file, data):
    """
    Insert provided data into the specified table using a .sql file
    :param conn: connection object
    :param sql_file: a .sql file containing the sql command
    :param data: a list of data
    :return: th unique identifier for the data
    """
    with open(sql_file, 'r') as file:
        sql = file.read()
    try:
        c = conn.cursor()
        c.execute(sql, data)
    except Error as e:
        print(e)
        sys.exit(0)
    
    return c.lastrowid


def create_view(conn, sql_file):
    """
    Executes a sql file
    :param conn: connection object
    :param sql_file: a .sql file containing the sql command
    :return: None
    """
    with open(sql_file, 'r') as file:
        sql = file.read()
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
        sys.exit(0)