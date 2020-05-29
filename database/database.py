import os
import pandas as pd
import numpy as np
from datetime import datetime
import time
import sys
from models import CreditCalculator
from models import PolicyTables
import sqlite3
from sqlite3 import Error
from arcpy import AddMessage
from components import (create_connection, create_table, insert_data, 
                        create_view)

# Hack in sql directory b/c Arc can't handle relative path names
sql_dir = os.path.join(sys.path[0], 'sql')

# Functions
def create_database(database_path):
    # create a database connection
    conn = create_connection(database_path)
    
    # create tables
    if conn is not None:        
        # Create list of table files
        tables = [table for table in os.listdir(sql_dir) 
                  if table.startswith('create_table')]
        
        # Create each table from list
        for table in tables:
            AddMessage('Running {}'.format(table))
            with open (os.path.join(sql_dir, table), 'r') as sql_file:
                sql = sql_file.read()
                create_table(conn, sql)
        
        conn.close()
        
    else:
        AddMessage ("Error! failed to create database connection.")

    
def import_credit_calc(database_path, credit_calc_file):
    database = database_path

    # create database connection
    conn = create_connection(database)
    
    # instantiate credit calculator object
    project_calc = CreditCalculator(credit_calc_file)
    
    # read in tables
    start = time.time()
    AddMessage('reading calculator at ' + credit_calc_file)
    map_units_df = project_calc.map_units_df
    current_ls_df = project_calc.current_ls_df
    projected_ls_df = project_calc.projected_ls_df
    transects_data_df = project_calc.transects_data_df
    mgmt_cats_df = project_calc.mgmt_cats_df
    wmz_df = project_calc.wmz_df
    pmu_df = project_calc.pmu_df
    precip_df = project_calc.precip_df
    desktop_results_df = project_calc.desktop_results_df
    field_sheets_df = project_calc.field_sheets_df
    field_info_df = project_calc.field_info_df
    shrubs_df = project_calc.shrubs_df
    # plot_df called for each plot when reading in data
    forb_grass_df = project_calc.forb_grass_df
    transects_review_df = project_calc.transects_review_df
    site_scale_values_df = project_calc.site_scale_values_df
    site_scale_scores_df = project_calc.site_scale_scores_df
    projected_values_df = project_calc.projected_values_df
    projected_scores_df = project_calc.projected_scores_df
    baseline_rr_inputs_df = project_calc.baseline_rr_inputs_df
    baseline_rr_df = project_calc.baseline_rr_df
    baseline_credits_df = project_calc.baseline_credits_df
    current_credits_df = project_calc.current_credits_df
    projected_credits_df = project_calc.projected_credits_df
    
    AddMessage('{} minutes elapsed'.format(round((time.time() - start)/60, 2)))
    start = time.time()
    
    # read in sql files
    AddMessage('reading sql files')
    map_units_sql = os.path.join(sql_dir, 'insert_map_units.sql')
    current_ls_sql = os.path.join(sql_dir, 'insert_current_ls.sql')
    projected_ls_sql = os.path.join(sql_dir, 'insert_projected_ls.sql')
    transect_data_sql = os.path.join(sql_dir, 'insert_transect_data.sql')
    mgmt_cats_sql = os.path.join(sql_dir, 'insert_project_mgmt_cats.sql')
    project_wmz_sql = os.path.join(sql_dir, 'insert_project_wmz.sql')
    project_pmu_sql = os.path.join(sql_dir, 'insert_project_pmu.sql')
    project_precip_sql = os.path.join(sql_dir, 'insert_project_precip.sql')
    desktop_results_sql = os.path.join(sql_dir, 'insert_desktop_results.sql')
    field_sheets_sql = os.path.join(sql_dir, 'insert_field_sheets.sql')
    field_info_sql = os.path.join(sql_dir, 'insert_field_info.sql')
    shrubs_sql = os.path.join(sql_dir, 'insert_shrub_data.sql')
    plots_sql = os.path.join(sql_dir, 'insert_plot_data.sql')
    forb_grass_sql = os.path.join(sql_dir, 'insert_forb_grass_data.sql')
    transects_review_sql = os.path.join(sql_dir, 'insert_transect_review.sql')
    site_scale_values_sql = os.path.join(sql_dir, 'insert_site_scale_values.sql')
    site_scale_scores_sql = os.path.join(sql_dir, 'insert_site_scale_scores.sql')
    projected_values_sql = os.path.join(sql_dir, 'insert_projected_values.sql')
    projected_scores_sql = os.path.join(sql_dir, 'insert_projected_scores.sql')
    baseline_rr_inputs_sql = os.path.join(sql_dir, 'insert_baseline_rr_inputs.sql')
    baseline_rr_sql = os.path.join(sql_dir, 'insert_baseline_rr.sql')
    baseline_credits_sql = os.path.join(sql_dir, 'insert_baseline_credits.sql')
    current_credits_sql = os.path.join(sql_dir, 'insert_current_credits.sql')
    projected_credits_sql = os.path.join(sql_dir, 'insert_projected_credits.sql')
    
    
    # plot cols (for reading in plot data)
    plot_cols =  {1: 'C:D, E:G', 
                  2: 'C:D, H:J',
                  3: 'C:D, K:M',
                  4: 'C:D, N:P',
                  5: 'C:D, Q:S'}
    
    # insert data into database
    with conn:
        AddMessage('inserting map units')
        for _, map_unit in map_units_df.iterrows():
            data = tuple(map_unit)
            insert_data(conn, map_units_sql, data)
        
        AddMessage('inserting current local-scale')
        for _, current_ls in current_ls_df.iterrows():
            data = tuple(current_ls)
            insert_data(conn, current_ls_sql, data)
        
        AddMessage('inserting projected local-scale')
        for _, projected_ls in projected_ls_df.iterrows():
            data = tuple(projected_ls)
            insert_data(conn, projected_ls_sql, data)
        
        AddMessage('inserting transect data')
        for _, transect in transects_data_df.iterrows():
            data = tuple(transect)
            insert_data(conn, transect_data_sql, data)
        
        AddMessage('inserting mgmt cats')
        for _, mgmt_cat in mgmt_cats_df.iterrows():
            data = tuple(mgmt_cat)
            insert_data(conn, mgmt_cats_sql, data)
        
        AddMessage('inserting wmz')
        for _, wmz in wmz_df.iterrows():
            data = tuple(wmz)
            insert_data(conn, project_wmz_sql, data)
        
        AddMessage('inserting pmu')
        for _, pmu in pmu_df.iterrows():
            data = tuple(pmu)
            insert_data(conn, project_pmu_sql, data)
        
        AddMessage('inserting precip')
        for _, precip in precip_df.iterrows():
            data = tuple(precip)
            insert_data(conn, project_precip_sql, data)
        
        print('inserting desktop results')
        for _, desktop_result in desktop_results_df.iterrows():
            data = tuple(desktop_result)
            insert_data(conn, desktop_results_sql, data)
        
        # for _, field_sheet in field_sheets_df.iterrows():
        #     data = tuple(field_sheet)
        #     insert_data(conn, field_sheets_sql, data)
        
        AddMessage('inserting field info')
        for _, field_info in field_info_df.iterrows():
            data = tuple(field_info)
            insert_data(conn, field_info_sql, data)
        
        AddMessage('inserting shrubs')
        for _, shrub in shrubs_df.iterrows():
            data = tuple(shrub)
            insert_data(conn, shrubs_sql, data)
        
        AddMessage('inserting plots')
        for plot_no in plot_cols:
            plot_df = project_calc.plot_df(plot_cols.get(plot_no))
            for _, plot in plot_df.iterrows():
                data = (plot_no,) + tuple(plot)
                insert_data(conn, plots_sql, data)
        
        AddMessage('inserting forbs and grasses')
        for _, forb_grass in forb_grass_df.iterrows():
            data = tuple(forb_grass)
            insert_data(conn, forb_grass_sql, data)
        
        print('inserting transect review')
        for _, transect_data in transects_review_df.iterrows():
            data = tuple(transect_data)
            insert_data(conn, transects_review_sql, data)
        
        print('inserting site scale values')
        for _, site_scale_value in site_scale_values_df.iterrows():
            data = tuple(site_scale_value)
            insert_data(conn, site_scale_values_sql, data)
        
        print('inserting site scale scores')
        for _, site_scale_score in site_scale_scores_df.iterrows():
            data = tuple(site_scale_score)
            insert_data(conn, site_scale_scores_sql, data)
        
        AddMessage('inserting projected values')
        for _, projected_value in projected_values_df.iterrows():
            data = tuple(projected_value)
            insert_data(conn, projected_values_sql, data)
        
        print('inserting projected scores')
        for _, projected_score in projected_scores_df.iterrows():
            data = tuple(projected_score)
            insert_data(conn, projected_scores_sql, data)
        
        AddMessage('inserting baseline and rr inputs')
        for _, baseline_rr_input in baseline_rr_inputs_df.iterrows():
            data = tuple(baseline_rr_input)
            insert_data(conn, baseline_rr_inputs_sql, data)
        
        print('inserting baseline and rr scores')
        for _, baseline_rr in baseline_rr_df.iterrows():
            data = tuple(baseline_rr)
            insert_data(conn, baseline_rr_sql, data)
        
        print('inserting baseline credits')
        for _, baseline_credit in baseline_credits_df.iterrows():
            data = tuple(baseline_credit)
            insert_data(conn, baseline_credits_sql, data)
        
        print('inserting current credits')
        for _, current_credit in current_credits_df.iterrows():
            data = tuple(current_credit)
            insert_data(conn, current_credits_sql, data)
        
        print('inserting projected credits')
        for _, projected_credit in projected_credits_df.iterrows():
            data = tuple(projected_credit)
            insert_data(conn, projected_credits_sql, data)
        
        AddMessage('{} minutes elapsed'.format(round((time.time() - start)/60, 2)))
    
    # USING FOREIGN KEYS
    # with conn:      
    #     # Locate sql instruction files
    #     m_sql_file = 'sql/insert_desktop_result.sql'
    #     t_sql_file = 'sql/insert_transect.sql'
    #     f_sql_file = 'sql/insert_field_info.sql'
        
    #     # Insert map unit
    #     print('Inserting map units')
    #     for _, m_data in desktop_results_df.iterrows():
    #         map_unit = list(m_data)
    #         map_unit_id = map_unit[0]
    #         map_unit_key = insert_data(conn, m_sql_file, map_unit)
        
    #         # Insert associated transects
    #         print(f'Inserting transects for map unit {map_unit_id}')
    #         transects = transects_data_df[transects_data_df[1] == map_unit_id]
    #         for _, t_data in transects.iterrows():
    #             transect = list(t_data)
    #             transect_id = transect[2]
    #             # Update the transect with the map_unit_key
    #             transect += (map_unit_key,)
    #             transect_key = insert_data(conn, t_sql_file, transect)
            
    #             # Insert associated field info (requires one:one relationship)
    #             field_info = field_info_df[field_info_df[3] == transect_id].to_numpy().tolist()[0]
    #             # Update the field info with transect_key
    #             field_info += (transect_key,)
    #             insert_data(conn, f_sql_file, field_info)
    
    conn.close()


def import_policy_tables(database_path, policy_tables_path):    
    database = database_path
    policy_tables_folder = policy_tables_path
    
    # create database connection
    conn = create_connection(database)

    # read in tables
    start = time.time()
    AddMessage('reading policy tables at ' + policy_tables_folder)
    for table in os.listdir(policy_tables_folder):
        # read in table
        table_path = os.path.join(policy_tables_folder, table)
        df = pd.read_csv(table_path)
        
        # read in sql file
        sql_file_name = 'insert_' + table[:-4].replace('-', '_') + '.sql'
        sql_file_path = os.path.join(sql_dir, sql_file_name)
        
        # insert data into database
        with conn:
            AddMessage('inserting ' + table[:-4].replace('-', '_'))
            for _, row in df.iterrows():
                data = tuple(row)
                insert_data(conn, sql_file_path, data)
    
    conn.close()
        
    AddMessage('{} seconds elapsed'.format(round((time.time() - start), 2)))
    

def create_views(database_path):
    database = database_path

    # create database connection
    conn = create_connection(database)
    
    # Create desktop results view
    AddMessage('creating desktop results view')
    view_desktop_results_sql = os.path.join(sql_dir, 'view_desktop_results.sql')
    create_view(conn, view_desktop_results_sql)
    
    # Create transect review view
    AddMessage('creating transects review')
    view_transect_sql = os.path.join(sql_dir, 'view_transect_data.sql')
    create_view(conn, view_transect_sql)
    
    # Create site scale values view
    view_map_unit_sql = os.path.join(sql_dir, 'view_site_scale_values.sql')
    create_view(conn, view_map_unit_sql)
    
    # Create reserve account view
    view_reserve_account_sql = os.path.join(sql_dir, 'view_reserve_account.sql')
    create_view(conn, view_reserve_account_sql)
    
    # Create baseline view
    view_baseline_sql = os.path.join(sql_dir, 'view_baseline.sql')
    create_view(conn, view_baseline_sql)
    
    conn.close()
    
        
def build_database(database_path, calculator_file,
                   policy_tables_path):
    create_database(database_path)
    import_credit_calc(database_path, calculator_file)
    import_policy_tables(database_path, policy_tables_path)
    create_views(database_path)
    
    
if __name__ == '__main__':
    database_path = 'test.db'
    calculator_file = None
    policy_tables_path = '../data/policy_tables'
    build_database(database_path, calculator_file,
                   policy_tables_path)
    
    
    