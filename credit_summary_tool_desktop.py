"""
Name:     credit_summary_tool_desktop.py
Author:   Erik Anderson
Created:  May 5, 2020
Revised:  May 5, 2020
Version:  Created using Python 2.7.10, Arc version 10.4.1
Requires: ArcGIS version 10.1 or later, Basic (ArcView) license or better

Copyright 2017-2020 Environmental Incentives, LLC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Script file is saved in AdminTools folder and run from AdminTools toolbox.
User provides output directory, map units, project name, and calculator file.
nv-ccs-database project must also be stored within AdminTools folder for 
import to this tool.

User should save a copy of the template in the output directory. A PDF report
will also be saved there.
"""

import arcpy
import os
import sys
import gc
import pandas as pd
import numpy as np
from reports import desktop_map_report
from database.models import CreditData
from database.database import build_database
from database.credit_calc import run_calculator, save_output
from database.scenario_calc import run_scenario_report
from reports import plotting

def main():
        
    # GET PARAMETER VALUES
    outputs = arcpy.GetParameterAsText(0)
    map_units_dissolve = arcpy.GetParameterAsText(1)
    project_calc = arcpy.GetParameterAsText(2)
    project_name = arcpy.GetParameterAsText(3)

    # DEFINE DIRECTORIES
    scriptPath = sys.path[0]
    arcpy.AddMessage("Script folder: " + scriptPath)
    arcpy.AddMessage("Python version: " + sys.version)
    
    # Define path to map template
    template_path = scriptPath.split('Lib')[0]
    # Define path to policy tables data
    policy_tables_path = os.path.join(scriptPath, 'data', 'policy-tables')
    # Sub in scriptPath for template_path as script should live in Admin
    # Define path to default geodatabase
    default_gdb = os.path.join(template_path, 'Scratch', 'scratch.gdb')
    arcpy.env.Workspace = default_gdb
    arcpy.env.scratchWorkspace = default_gdb
    
    # ENVIRONMENT SETTINGS
    # Overwrite outputs
    arcpy.env.overwriteOutput = True
    
    # ------------------------------------------------------------------------
    
    arcpy.AddMessage('creating database, please be patient')
    # Create database, read in calculator and policy tables
    database_path = os.path.join(outputs, project_name + '.db')
    # build_database(database_path, project_calc,
    #                policy_tables_path)
    
    # arcpy.AddMessage('database created')
    
    # Instantiate CreditData object
    C = CreditData(db=database_path)
    
    arcpy.AddMessage('calculating credits')
    
    # Retrieve projected credit report
    current_credits, projected_credits = run_calculator(C)
    
    arcpy.AddMessage('building report')
    
    # Build map reports
    desktop_map_report.generate_reports(
        map_units_dissolve,
        default_gdb, 
        template_path,
        project_name,
        outputs,
        projected_credits
    )
    
    # Get scenario results
    scenario_report = run_scenario_report(C)
    save_output(outputs, scenario_report, 'scenario_report.csv')
    
    # Create and save plots
    current_data = current_credits
    proj_data = projected_credits
    projcredits = proj_data[['map_unit_id', 'saleable_credits']]
    projcredits.rename(columns = {'saleable_credits': 'proj_credits'}, inplace= True)
    
    plotting.update_pdf(
        outputs, 
        current_data,
        proj_data,
        scenario_report
    )
    
    C.conn.close()
    
    
# EXECUTE SCRIPT

if __name__ == "__main__":
    gc.enable()
    main()
    gc.collect()
