"""
Name:     Admin_Transect_Tool.py
Author:   Erik Anderson
Created:  June 6, 2019
Revised:  June 6, 2019
Version:  Created using Python 2.7.10, Arc version 10.4.1
Requires: ArcGIS version 10.1 or later, Basic (ArcView) license or better;

Saves output as shapefile in specified folder

"""

# Import system modules
import arcpy
import random
import sys
import gc


def main():
    # GET PARAMETER VALUES
    Transects_Provided = arcpy.GetParameterAsText(0)
    Transects_Workspace = arcpy.GetParameterAsText(1)
    Project_Name = arcpy.GetParameterAsText(2)

    # Create geodatabase for output
    existing_gdbs = arcpy.ListWorkspaces(workspace_type='FileGDB')
    existing_gdbs_lower = [each.lower for each in existing_gdbs]
    if Project_Name.lower() in existing_gdbs_lower:
        arcpy.AddError("File Geodatabase name " + Project_Name + " already"
                       + "exists. Please rename and try again.")
        sys.exit(0)
    gdb = arcpy.CreateFileGDB_management(Transects_Workspace,
                                         Project_Name, "10.0")

    # ENVIRONMENT SETTINGS
    # Set workspaces
    arcpy.AddMessage(arcpy.Describe(gdb).catalogPath)
    arcpy.env.workspace = arcpy.Describe(gdb).catalogPath
    arcpy.env.scratchWorkspace = arcpy.Describe(gdb).catalogPath
    # Overwrite outputs
    arcpy.env.overwriteOutput = True

    # ------------------------------------------------------------------------

    def AddTransectFields(transects):
        arcpy.AddMessage("Generating Transect ID")
        id_field = "sample"
        new_field = "Transect_Number"
        existing_fields = arcpy.ListFields(transects)
        existing_fields_lower = [each.name.lower() for each in existing_fields]
        # For debit projects, just delete id_field
        if (new_field.lower() in existing_fields_lower and 
            id_field.lower() in existing_fields_lower):   
            arcpy.DeleteField_management(transects, id_field)
        # For credit projects, rename id_field to Transect_Number
        elif id_field.lower() in existing_fields_lower:
            arcpy.AlterField_management(transects, id_field, new_field,
                                        clear_field_alias=True)
        
        
        arcpy.CopyFeatures_management(transects, "after_id")

        # Rename for UTM
        arcpy.AddMessage("Calculate the UTM Easting and Northing for each transect")
        coord_fields = ["xcoord", "ycoord"]
        rename_fields = ["UTM_E", "UTM_N"]
        for existing, rename in zip(coord_fields, rename_fields):
            arcpy.AddField_management(transects, rename, "DOUBLE")
            with arcpy.da.UpdateCursor(transects, [existing, rename]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row)

        # Add fields for Bearing
        arcpy.AddMessage("Generate random bearing directions for each transect")
        fields_to_add = ["Bearing1", "Bearing2", "Bearing3"]
        field_types = ["SHORT", "SHORT", "SHORT"]
        field_types_dict = dict(zip(fields_to_add, field_types))
        for field in fields_to_add:
            arcpy.AddField_management(transects, field,
                                      field_types_dict[field])
        with arcpy.da.UpdateCursor(transects, fields_to_add) as cursor:
            for row in cursor:
                row[0] = random.randint(0, 360)
                row[1] = random.randint(0, 360)
                row[2] = random.randint(0, 360)
                cursor.updateRow(row)

        # Add fields for Sample_Type 
        arcpy.AddMessage("Creating Sample_Type field")
        fields_to_add = ["Sample_Type"]
        field_types = ["TEXT"]
        existing_fields = arcpy.ListFields(transects)
        existing_fields_lower = [each.name.lower() for each in existing_fields]
        # If existing (debit projects only), copy to end of table to preserve order
        if fields_to_add[0].lower() in existing_fields_lower:
            arcpy.AddField_management(transects, fields_to_add[0] + "2", field_types[0])
            with arcpy.da.UpdateCursor(transects, [fields_to_add[0], fields_to_add[0] + "2"]) as cursor:
                for row in cursor:
                    row[1] = row[0]
                    cursor.updateRow(row) 
            arcpy.DeleteField_management(transects, fields_to_add[0])
            arcpy.AlterField_management(transects, fields_to_add[0] + "2", fields_to_add[0])     
        else:
            field_types_dict = dict(zip(fields_to_add, field_types))
            for field in fields_to_add:
                arcpy.AddField_management(transects, field,
                                          field_types_dict[field])

            # Update all Sample_Type fields with default as 'Sample'
            with arcpy.da.UpdateCursor(transects, fields_to_add[0]) as cursor:
                for row in cursor:
                    row[0] = "Sample"
                    cursor.updateRow(row)
        
        # Add fields for Notes
        arcpy.AddMessage("Creating Notes fields")
        fields_to_add = ["Notes"]
        field_types = ["TEXT"]
        existing_fields = arcpy.ListFields(transects)
        existing_fields_lower = [each.name.lower() for each in existing_fields]
        for field in fields_to_add:
            if field.lower() in existing_fields_lower:
                arcpy.DeleteField_management(transects, field)
        field_types_dict = dict(zip(fields_to_add, field_types))
        for field in fields_to_add:
            arcpy.AddField_management(transects, field,
                                      field_types_dict[field])

    # ------------------------------------------------------------------------

    # Copy provided to geodatabase
    save_name = Project_Name + "_Transects"
    transects_copy = arcpy.CopyFeatures_management(
        Transects_Provided, "in_memory/tmp"
    )

    # Adjust transect table
    AddTransectFields(transects_copy)

    # Delete unneccessary fields    
    allowable_fields = ["Transect_Number",
                       "UTM_E", "UTM_N",
                       "Bearing1", "Bearing2", "Bearing3",
                       "Sample_Type", "Notes"]
    for field in arcpy.ListFields(transects_copy):
        if field.name not in allowable_fields \
                and field.required is False:
            try:
                arcpy.DeleteField_management(transects_copy, field.name)
            except arcpy.ExecuteError:
                pass
    
    # Sort fields by Transect ID
    arcpy.Sort_management(transects_copy, save_name,
                        [["Transect_Number", "ASCENDING"]])
            
    # ------------------------------------------------------------------------

if __name__ == "__main__":
    gc.enable()
    main()
    gc.collect()
