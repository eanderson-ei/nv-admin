# README

This library reads the NV CCS Credit Project Calculator v1.6 into a database. The intent of this library is to evolve to serve as the Registry Database. For now, it serves as an efficient means of reading a single Project Calculator.

Save the Project Calculator within `data/external/` and specify path in `calc_credits.py`.

Recommend downloading [SQLite Studio](https://sqlitestudio.pl/) for exploring the database.



## Contents

**initialize_database.bat**: a convenience batch file for initializing the database. Creates a database `test.db` in the root folder. Delete the existing database before running.

**scripts/**

* **010_create_database_calc.py**: creates a database including any table described by a file in the `sql/` folder starting with 'create_table'
* **020_import policy_tables.py**: imports policy tables to the database with versioning
* **030_import credit_calc.py**: reads a Project Calculator and stores data in the database created by `create_database.py`
* **040_create_views.py**: creates views for transect-level roll ups, map-unit-level roll ups, and credit-level roll ups for all projects in the database.
* **models.py**: includes classes:
  * `CreditCalculator` where each property describes how to read from the correct tab of the Project Calculator to create a pandas data frame from the data
  * `PolicyTables` reads policy tables into an object for convenient reference by version.
* **calc_credits.py**: creates a credit report for current and projected conditions using tables from the database. Saves reports to `data/processed/`. A table of projected values may be provided (see user defined inputs).

**sql/**

* all DDL and DML sql statements as `.sql` files. Use the conventions: 
  * start a *create table* command with `create_table`, 
  * start an *insert* command with `insert`, and 
  * start a *view* command with `view`.

**tests/**

* **compare_table_insert.py**: ensures a `create_table` and corresponding `insert` sql statement have the same number of attributes, *modify the primary and secondary key variables if needed*.

## Design

### Inputs

The final version should take as input the outputs of the GIS process and the field datasheets. All other tables should be calculated as views. The database will also store scoring curves and policy tables for each version of the calculator. Projected site-scale values are read in from the Calculator for now.

* Project Data (data/external/)
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
	* validation lists (precipitation regime, mgmt cat, r&r, wildfire, competing land use, sage species, shrub species, conifer, sample type)

### Flow

1. Create a database that will contain the desired tables. The database must be created first, and separate from reading data, to allow for multiple data sources (e.g., field sheets, Project Calculators) to be read into the same database.
2. Import Policy tables. Save version. (Don't repeat table if it hasn't changed, add table for cross-referencing valid tables). Tidy data.
3. Import Project data. Save foreign keys while reading in data to correlate data with the transect, map unit, and/or project.
   1. To start over by dropping all tables without re-creating the schema, use the command `sqlite3 <db_name.db>` to enter a sqlite3 session and then `.read sql/drop_all_tables.sql` followed by `.quit` to exit.
4. Roll up data to calculate at the transect, and then map unit, scale. Use SQL statements to create [Views](https://www.sqlitetutorial.net/sqlite-create-view/), renaming columns as necessary. These data should be in tidy format. Views are calculated on-the-fly for any project, minimizing storage required. Views will mimic blue tabs in Calculator.
5. Calculate scores and credits at the map unit scale for each season for current and projected condition. Honor HQT version. Read in Views as Pandas tables for efficient manipulation (high level programming languages are better than SQL for readability, testing, etc.). Modularize this script so that any table of habitat attribute values can be scored and then compared to any other set of habitat attribute values.
6. Create reports as needed (instances of Views) for reporting. These need not be tidy.

### Outputs

#### Calculated tables

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

* Arcpy cannot parse paths with .. and ., instead I needed to use sys.path[0] to get the path from which the tool was run and use that to 'hack' in paths that were once relative. Note that sys.path[0] always gives the path of the toolbox, regardless of which nested module it is encountered in.
  * Database.py has this at the top
* To allow for easier import of packages, I
  * combined the nvccs-database project in the database folder and 
  * combined the nvccs-credit-summary project in the reports folder, 
  * moved the script associated with the tool up to the root (called Lib)
  * combined all four scripts used to create the database in a single file 'database.py' as functions of the same name. 'build_database' in that module now runs the four in sequence.
* For faster import, I am only importing the necessary inputs from the Calculator (extra code is commented out, not deleted)