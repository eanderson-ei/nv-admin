# README

Clone as `Lib` into `NevadaAdminTools/`

Recommend downloading [SQLite Studio](https://sqlitestudio.pl/) for exploring the database.

Changes to plotting.py: 

Line 95

```
save_name = os.path.join(workspace, 'full_summary_chart.pdf')
chartone = fig.savefig(save_name, bbox_inches='tight')
```

Line 210

```
save_name = os.path.join(workspace, 'managementregime_summary_chart.pdf')
regminepdf = fig.savefig(save_name, bbox_inches='tight')
```

Line 324

```
save_name = os.path.join(workspace, '{}_summarypage1.pdf'.format(i))
summary1 = fig.savefig(save_name, bbox_inches='tight', papertype = 'letter')       
```

Line 330

```
title_page = os.path.join(workspace, 'title_page.pdf')
pdfDoc1 = arcpy.mp.PDFDocumentOpen(title_page)
```

Line 337

```
map_series_loc = os.path.join(workspace, 'series.pdf')
series = arcpy.mp.PDFDocumentOpen(map_series_loc)
```

Breaking changes for pandas 0.16

pd.sort (instead of pd.sort_values) in plotting.py 

## Contents

**database/**

*This library reads the NV CCS Credit Project Calculator v1.6 into a database. The intent of this library is to evolve to serve as the Registry Database. For now, it serves as an efficient means of reading a single Project Calculator for the Credit Summary Tool.*

* **components.py**: base level sqlite functions for creating database, inserting data, and creating views. These are shared by `database.py` and `models.py`, so to avoid circular imports they are partitioned here, rather than combined with `database.py`.
* **database.py**: all functions required to create and update the database. The database is populated with only the data from the calculator required to calculate credits. Policy tables are read in from the `data/policy-tables` folder.  In this version, a unique database is created in the project workspace for each project.
* **models.py**: includes classes:
  * `CreditCalculator` where each property describes how to read from the correct tab of the Project Calculator to create a pandas data frame from the data
  * `CreditData` object to access the database data for a single project.
* **calc_credits.py**: creates a credit report for current and projected conditions using tables from the database. A table of projected values may be provided, else the projected values in the Calculator is used.
* **scenario_calc.py**: defines scenarios and creates a scenario report where each scenario is a column and the saleable credits created for each map unit are the values.

**sql/**

* all DDL and DML sql statements as `.sql` files. Use the conventions: 
  * start a *create table* command with `create_table`, 
  * start an *insert* command with `insert`, and 
  * start a *view* command with `view`.

**reports/**

* **desktop_map_report.py**: generates a title page and map series for the Credit Summary Tool using Python 2 and the Desktop environment for `arcpy`.
* **pro_map_report.py**: generates a title page and map series for the Credit Summary Tool using Python 3 and the Pro environment for `arcpy`.
* **plotting.py**: generates PDF reports with charts for the Credit Summary Tool. Uses Python 2 for compatibility with Desktop.

**tests/**

* **compare_table_insert.py**: ensures a `create_table` and corresponding `insert` sql statement have the same number of attributes, *modify the primary and secondary key variables if needed*.

**data/policy-tables**: Contains all policy tables for v1.6 of the HQT

## Design

### Inputs

The final version should take as input the outputs of the GIS process and the field datasheets. All other tables should be calculated as views. The database will also store scoring curves and policy tables for each version of the calculator. Projected site-scale values are read in from the Calculator for now.

* Project Data (from a v1.6 Credit Calculator)
  * _Map_Units excel sheet
  * _WMZ, _PMU, _MGMT, _PRECIP sheets
  * field_info
  * shrubs
  * forbs and grasses
  * plots
  * projected_values
* Policy (data/policy-tables/)
  * scoring curves
  * policy tables (cover classes, scoring weights, baselines, reserve account, mgmt multipliers, meadow multiplier, R&R Score, Wildfire score)
  * validation lists (precipitation regime, mgmt cat, r&r, wildfire, competing land use, sage species, shrub species, conifer, sample type). NOT IMPLEMENTED.

### Flow

User should open the map template and save it into a new, unique workspace before running the Credit Summary Tool, passing as inputs the workspace location, the map_units_dissolve shapefile or feature class, the Credit Calc, and optionally a save name.

1. Create a database that will contain the desired tables. (Eventually, the database will be common to all projects, for now it is unique to the project assessed).
2. Import Policy tables. Save version. (Don't repeat table if it hasn't changed, add table for cross-referencing valid tables). Tidy data.
3. Import Project data. Save foreign keys while reading in data to correlate data with the transect, map unit, and/or project.
   1. To start over by dropping all tables without re-creating the schema, use the command `sqlite3 <db_name.db>` to enter a sqlite3 session and then `.read sql/drop_all_tables.sql` followed by `.quit` to exit.
4. Roll up data to calculate at the transect, and then map unit, scale. Use SQL statements to create [Views](https://www.sqlitetutorial.net/sqlite-create-view/), renaming columns as necessary. These data should be in tidy format. Views are calculated on-the-fly for any project, minimizing storage required. Views will mimic blue tabs in Calculator.
5. Calculate scores and credits at the map unit scale for each season for current and projected condition. Honor HQT version (NOT IMPLEMENTED). Read in Views as Pandas tables for efficient manipulation (high level programming languages are better than SQL for readability, testing, etc.). Modularize this script so that any table of habitat attribute values can be scored and then compared to any other set of habitat attribute values.
6. Create title page and map series as PDFs, save into workspace.
7. Evaluate scenarios and create charts as PDFs for each scenario.

#### Intermediate tables available

##### Views in database

1. **view_desktop_results**: summary of GIS data needed to calculate credits. Excludes PMU/BSU breakdown. 
2. **view_transect_data**: roll up of field data to transect level
3. **view_site**-scale_values: roll up of field data to map unit level
4. **view_reserve_account**: reserve account required by map unit
5. **view_baseline**: regional standard baseline values by map unit

##### Dataframes from credit_calc.py

1. **current_site_scale**: site scale values scored, weighted and combined by season
2. **current_facres**: f-acres per map unit for current condition (similar to 3.1 View Credit Results) 
3. **baseline_corrected**: baseline scores where lower site-scale scores are substituted for regional standard baseline per map unit
4. **baseline_facres**: f-acres per map unit using corrected baseline values
5. **current_credits**: credits resulting from difference between baseline and current conditions. Saved out to `data/processed/`
6. **projected_site_scale**: site scale values with projected values are substituted for current where provided
7. **projected_scores**: site scale scores for projected condition
8. **projected_facres**: f-acres per map unit for projected condition
9. **projected_credits**: credits resulting from difference between projected and current conditions. Saved out to `data/processed/`

### Outputs

* Map Book as pdf with title page, summary chart, scenario charts, and map series. 
* Updated map template
* Project database

## Tips

Try SchemaCrawler to create an ERD diagram if needed. See example [here](https://blog.stefanproell.at/2016/01/11/create-an-er-diagram-of-an-existing-sqlite-database-or-manyoother-rdbms/). You'll need to [install Java](https://java.com/en/download/manual.jsp) and add to your PATH.

---

An alternative to unstacking the wmz, pmu, mgmt, precip tables would be to left outer join the scores for each hab_attr on the map_unit_id and moisture_regime column and sum along the map_unit_id and hab_attr

```
map_unit_id, moisture_regime, proportion, attribute, score, (weighted_score);
1, arid, 40%, b_forb_cover, 60%, (24%);
1, mesic, 60%, b_forb_cover, 65%, (37%);
```

becomes

```
1, b_forb_cover, 61%;
```

This is more natural for `SQL`, but less so for `pandas`. Use this to calculate credits per WMZ, PMU, or BSU. Use unstacking to get proportions needed for calculating credits in the first place.

---

Sqlite 3 does not have a boolean data type, rather stores True/False as 1/0. Maintain this behavior (as opposed to 'True', 'False' as text) as a standard. In pandas, convert boolean data types to int and then to boolean to block for reading as an object. (`.astype('int').astype('bool')`)

---

For some reason, between sessions my simple .bat file stopped working. It probably was finding a different install of python and missing the xlrd package (although I think both of my python installs include xlrd). Ideally, I'd be working in a conda environment and the .bat file would activate it first. Here's some code that might work:

```
call activate [my_env]
python my_script.py
call conda deactivate
```

This will require that anyone else using the batch file also has replicated my environment. First, to export the environment:

`conda list --explicit > <environment name>.txt`

To create from this text file

`conda env create --file <environment name>.txt` or `conda create --name <name> --file <file name>.txt`

This [conda cheat sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf) is great.

## Next Steps

- [x] Design policy tables schema and coding conventions
- [x] Import policy tables for 1.6
- [x] Import GIS data
- [x] Create view for Desktop Results
- [x] Import baseline & rr data
- [x] Create View for baseline & rr ratings (view_baseline, view_reserve_account)
- [ ] Create View for seasonal scores from field data (view_site_scale_scores)
- [ ] Create View for credits from seasonal scores and policy info
- [ ] Add submission id to project id crosswalk table
- [ ] Add project id table
- [ ] Add submission id to all credit project create table and insert sql files
- [ ] Read tables sequentially to include submission id
- [ ] update credit calcs with hqt version support
- [ ] *draft notebook to describe scoring methods

### TODO

- [ ] add mgmt_multiplier to desktop results view, remove from credit report
- [ ] block if no_transects is 0 to avoid DIV BY ZERO error
- [ ] simplify fields in views (e.g., meadow, map unit name) to avoid duplication
- [ ] when removing duplicates for seasonal projected values, use the value with the highest score, rather than the average value


### NOTES 

- My version of ArcGIS Desktop is using Python 2.7 and Pandas 0.16.1! To make this backwards compatible, the following changes were made:
  - Convert all f-strings to .format()
  - Change kwarg 'usecols' in pd.read_excel to 'parsecols'
  - For projected credits, call pd.melt instead of df.melt (not yet a method of the dataframe class)

* Arcpy cannot parse paths with `..` and `.`, instead I needed to use sys.path[0] to get the path from which the tool was run and use that to 'hack' in paths that were once relative. Note that sys.path[0] always gives the path of the toolbox, regardless of which nested module it is encountered in.
  * `database.py` has this at the top
* To allow for easier import of packages, I
  * combined the nvccs-database project in the database folder and 
  * combined the nvccs-credit-summary project in the reports folder, 
  * moved the script associated with the tool up to the root (called Lib)
  * combined all scripts used to create the database in a single file `database.py` as functions of the same name. `build_database.py` in that module now runs the four in sequence, using the utility functions that were in `components.py`.
* For faster import, I am only importing the necessary inputs from the Calculator (extra code is commented out, not deleted)

# EI-DEV Notes

### How to set up arcdesktop environment

Arc Desktop 10.4 ships with Python 2.7.10 (which includes sqlite3 3.6.1), Pandas 0.16.1, and Matplotlib 1.4.3. There are a few breaking changes between those versions and the most recent versions of those packages. Thus, it's helpful to set up a virtual environment when working with those packages so that errors are caught earlier in the process.

The Pandas 0.16 manual is here, you'll need that to use older versions of functions like pd.sort_values or pd.melt.

You'll want to use virtualenv to set up this environment. venv won't work because you need to specify a specific version of python. This environment can be created anywhere, but we'll create it in the root project folder for now.

You may need to install virtualenv since it does not come with the conda distribution (`conda install -c conda-forge virtualenv`). 

To create this environment with a copy of the Python distribution you got with ArcDesktop, you need to find the executable Python file associated with Arc. Mine was located at `C:/Python27/ArcGIS10.4/Lib/python.exe`

Open the Anaconda prompt in the project's root and type:

```
virtualenv <NAME> python=C:/Python27/ArcGIS10.4/Lib/python.exe
```

the <NAME> you choose will be created as a directory in the project's folder.

Install packages using pip

```
pip install pandas==0.16.1
pip install matplotlib==1.4.3
```

You can check which versions of pandas or matplotlib your distribution of ArcDesktop has by using the Python interpreter window in ArcMap. Use these commands:

```python
import pandas
pandas.__version__
import matplotlib
matplotlib.__version__
```

Next, you'll need to allow this environment to access the `arcpy` module, which you can't pip install since it is not open source.

1. navigate to the site-packages directory within the Python folder distributed with ArcDesktop. Mine was at `C:/Python27/ArcGIS10.4/Lib/site-packages/.
2. Copy the file called 'Desktop10.4.pth'
3. Paste it in the virtual environment folder you created (`~<NAME>/Lib/site-packages`). This will allow the environment to resolve where the arcpy module is without needing to copy it over. Keep in mind you will still need a license to run this module.