import os
from components import create_connection, create_table


def create_database(database_path):
    
    # create a database connection
    conn = create_connection(database_path)
    
    # create tables
    if conn is not None:        
        # Create list of table files 
        tables = [table for table in os.listdir('sql') 
                  if table.startswith('create_table')]
        
        # Create each table from list
        for table in tables:
            print(f'Running {table}')
            with open (os.path.join('sql', table), 'r') as sql_file:
                sql = sql_file.read()
                create_table(conn, sql)
        
        conn.close()
        
    else:
        print ("Error! failed to create database connection.")

if __name__ == '__main__':
    database_path = 'test.db'
    create_database(database_path)
    