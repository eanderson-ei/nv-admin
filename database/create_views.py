from components import create_connection, create_view
import pandas as pd
import numpy as np
import sys



def create_views(database_path):
    database = database_path

    # create database connection
    conn = create_connection(database)
    
    # Create desktop results view
    view_desktop_results_sql = 'sql/view_desktop_results.sql'
    create_view(conn, view_desktop_results_sql)
    
    # Create transect review view
    view_transect_sql = 'sql/view_transect_data.sql'
    create_view(conn, view_transect_sql)
    
    # Create site scale values view
    view_map_unit_sql = 'sql/view_site_scale_values.sql'
    create_view(conn, view_map_unit_sql)
    
    # Create reserve account view
    view_reserve_account_sql = 'sql/view_reserve_account.sql'
    create_view(conn, view_reserve_account_sql)
    
    # Create baseline view
    view_baseline_sql = 'sql/view_baseline.sql'
    create_view(conn, view_baseline_sql)
    
    conn.close()


if __name__ == '__main__':
    database_path = 'test.db'
    create_views(database_path)