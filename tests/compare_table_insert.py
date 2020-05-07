import os

for filename in os.listdir('sql/'):
    if filename.startswith('create_table'):
        create_table_sql = filename
        table_name = filename.split('create_table_')[1].split('.sql')[0]
        insert_sql = 'insert_' + table_name + '.sql'
        # Provide sql files to compare, one for the create table and 
        # one for the insert statement
        table_sql_file = os.path.join('sql', create_table_sql)
        insert_sql_file = os.path.join('sql', insert_sql)

        # Indicate the number of primary and/or foreign keys (True/False acceptable if only one)
        pkey = False
        fkey = False
        if table_name in []:
            pkey = True
        if table_name in []:
            pkey = True
            fkey = True       

        # Read in tables
        with open(table_sql_file, 'r') as file:
            table_sql = file.read()

        with open(insert_sql_file, 'r') as file:
            insert_sql = file.read()

        # Coerce to list
        table_columns = table_sql.strip().split('\n')[1:-1]
        insert_data = insert_sql.strip().split('\n')[1:-1]
        insert_spaces = insert_sql.strip().split('\n')[-1].count('?')

        # Print length of each variable
        print(table_name)
        print(len(table_columns))
        print(len(insert_data))
        print(insert_spaces)

        # Test if length of insert statement is same as length of table
        assert(len(table_columns) == len(insert_data) + pkey + fkey)

        # Test if insert statement has sufficient '?'
        assert(len(insert_data) == insert_spaces)

        # Print success message if no error
        print('Passes')


