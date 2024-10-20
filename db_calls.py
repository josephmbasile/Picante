import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful.")
    except Error as e:
        print(f"""An error occured: {e}""")

    return connection

def execute_query(connection, query):
    """Write databse query."""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        success_message = f"""Query executed successfully"""
        #print(success_message)
        return success_message

    except Error as e:
        print(f"""An error occured: {e}""")
        return e


def execute_read_query(connection, query):
    """Returns a list of tuples from the database."""
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"""An error occured: {e}""")

def execute_read_query_tuple(connection, query):
    """Returns a list of dictionary objects from the database."""
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    results = None
    try:
        cursor.execute(query)
        results = tuple(zip(cursor.fetchall()))
        res_dicts = [
            result
            for result in results
            #dict(zip(result[i].keys(),result[i]))
        ]
        return res_dicts
    except Error as e:
        print(f"""An error occured: {e}""")


def execute_read_query_dict(connection, query):
    """Returns a list of dictionary objects from the database."""
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    results = None
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        res_dicts = [
            dict(zip(result.keys(),result))
            for result in results
            #dict(zip(result[i].keys(),result[i]))
        ]
        return res_dicts
    except Error as e:
        print(f"""An error occured: {e}""")
