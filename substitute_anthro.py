"""
Name:     Admin_Tools/Substitute_Anthro.py
Author:   Erik Anderson
Created:  November 21, 2019
Revised:  November 21, 2019
Version:  Created using Python 2.7.10, Arc version 10.4.1
Requires: ArcGIS version 10.1 or later, Basic (ArcView) license or better;

Replaces a provide anthropogenic feature layer with another while preserving
subtypes.
Subtype names must be the same as the default value for the Subtype field for that
subtype.
Subtype domains must be named as the basename of the feature (e.g., "Roads") appended
with "_Subtypes".
The default Type value must be the same as the basename of the feature (e.g., "Roads")
"""

import arcpy
import sys

def main():
    # GET PARAMETER VALUES
    New_Anthro_Features = arcpy.GetParameterAsText(0)
    Existing_Anthro_Features = arcpy.GetParameterAsText(1)
    replace_subtypes = arcpy.GetParameterAsText(2)
    
    # Overwrite outputs
    arcpy.env.overwriteOutput = True
    
    # Helper functions (from ccslib)
    def Str2Bool(string):
        """
        Converts a string to Python boolean. If not 'true' in lowercase, returns
        False.
        :param string: a string of True or False, not cap sensitive
        :return: Boolean
        """
        if string == 'True' or string == 'true':
            return True
        else:
            return False
    
    def AddFields(input_feature, field_to_add, field_types, copy_existing=False):
        """
        Adds provided fields to the input_feature, removes or copies existing of
        the same name.
        :param input_feature: a feature class
        :param field_to_add: a list of field names as strings
        :param field_types: a list of field types as strings, in order of fields_
        to_add
        :param copy_existing: True to create a copy of any existing field with
        same name as field to add
        :return: None
        """
        
        # Create dictionary of field types mapped to fields to add
        fieldTypesDict = dict(zip(field_to_add, field_types))

        # Copy fields if they exist and delete original
        existingFields = arcpy.ListFields(input_feature)
        fieldNames = [each.name.lower() for each in existingFields]
        for field in field_to_add:
            if field.lower() in fieldNames:
                arcpy.AddMessage(field + " field exists.")
                if copy_existing:
                    arcpy.AddMessage("Copying to new field named " + field
                                    + "_copy.")
                    fieldIndex = fieldNames.index(field.lower())
                    if field.lower() + "_copy" in fieldNames:
                        arcpy.AddMessage("Deleting field " + field + "_copy")
                        arcpy.DeleteField_management(input_feature,
                                                    field + "_copy")
                    arcpy.AddField_management(input_feature, field + "_copy",
                                            existingFields[fieldIndex].type)
                    with arcpy.da.UpdateCursor(
                            input_feature, [field, field + "_copy"]) as cursor:
                        try:
                            for row in cursor:
                                row[1] = row[0]
                                cursor.updateRow(row)
                        except arcpy.ExecuteError:
                            arcpy.AddMessage("Unable to copy from " + field
                                            + " to " + field + "_copy.")
                arcpy.AddMessage("Deleting original field.")
                arcpy.DeleteField_management(input_feature, field)

        # Add fields
        for field in field_to_add:
            # arcpy.AddMessage("Adding " + field + " field")
            arcpy.AddField_management(input_feature, field,
                                    fieldTypesDict[field],
                                    field_length=50)
    
    # Main script
    
    # Get path to existing anthro features
    desc = arcpy.Describe(Existing_Anthro_Features)
    anthro_feature_path = desc.catalogPath
    
    # List subtypes from the existing anthro features
    subtypes = arcpy.da.ListSubtypes(Existing_Anthro_Features)
    
    # Add new field "Feature"
    AddFields(New_Anthro_Features, ['Feature'], ['SHORT'])
    
    # Copy new features over existing
    feature = arcpy.CopyFeatures_management(New_Anthro_Features, anthro_feature_path)

    replace_subtypes = Str2Bool(replace_subtypes)

    if replace_subtypes:        
        # Set Feature field to Subtype field
        arcpy.SetSubtypeField_management(feature, "Feature")
        
        # Create subtypes
        for stcode, stdict in list(subtypes.items()):
            arcpy.AddSubtype_management(
                feature, stcode, stdict['Name']
                )
        
        # Iterate through subtypes and update feature code
        def get_feature_code(subtype_name):
            for stcode, stdict in list(subtypes.items()):
                if stdict['Name'] == subtype_name:
                    return stcode
        
        with arcpy.da.UpdateCursor(feature, ["Feature", "Subtype"]) as cursor:
            for row in cursor:
                row[0] = get_feature_code(row[1])
                cursor.updateRow(row)        
        
        # Apply domains
        feature_basename = desc.baseName
        domain_name = feature_basename + "_Subtypes"
        
        arcpy.AssignDomainToField_management(feature, "Subtype", domain_name)
        if len(subtypes) == 1 and subtypes[0]['SubtypeField'] == '':
            pass
        else:
            st_codes = [str(stcode) for stcode, stdict in list(subtypes.items())]
            arcpy.AssignDomainToField_management(feature, "Subtype", domain_name, 
                                                 st_codes)
        
        # Apply defaults
        for st_code, st_dict in list(subtypes.items()):
            default = subtypes[st_code]['Name']
            arcpy.AssignDefaultToField_management(feature, "Subtype", default, st_code)
        
        default_type = feature_basename
        st_codes = [str(stcode) for stcode, stdict in list(subtypes.items())]
        arcpy.AssignDefaultToField_management(feature, "Type", default_type, st_codes)

if __name__ == '__main__':
    main()