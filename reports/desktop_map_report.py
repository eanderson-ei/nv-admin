# FUNCTIONS
"""
Name:     desktop_map_report.py
Author:   Erik Anderson
Created:  May 7, 2020
Revised:  May 7, 2020
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

"""

import arcpy
import os
import sys
import pandas as pd
import numpy as np

def AddToMap(feature_or_raster, layer_file=None, zoom_to=False):
    """
    Adds provided to the map document after removing any layers of the same
    name.
    :param feature_or_raster: feature class or raster dataset
    :param layer_file: layer file
    :param zoom_to: True to zoom to the added object
    :return: None
    """
    # Add layer to map
    arcpy.AddMessage("Adding layer to map document")
    if arcpy.ListInstallations()[0] == 'arcgispro':
        p = arcpy.mp.ArcGISProject("CURRENT")
        m= p.activeMap
        layer_path = arcpy.Describe(feature_or_raster).catalogPath #arcpy.Describe calls metadata, so this gives full path
        for existingLayer in m.listLayers(m):
            if existingLayer.name == feature_or_raster:
                m.remove_layer(existingLayer)
        m.addDataFromPath(layer_path)
        # TODO: revisit layer file application in Pro.
        if layer_file:
            arcpy.ApplySymbologyFromLayer_management(feature_or_raster, layer_file)
        #if zoom_to:
        #   m.extent = layer.getSelectedExtent()
        del p, m

    else:
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = mxd.activeDataFrame
        layer_path = arcpy.Describe(feature_or_raster).catalogPath
        layer = arcpy.mapping.Layer(layer_path)
        for existingLayer in arcpy.mapping.ListLayers(mxd, "", df):
            if existingLayer.name == layer.name:
                arcpy.mapping.RemoveLayer(df, existingLayer)
        arcpy.mapping.AddLayer(df, layer)
        if layer_file:
            arcpy.ApplySymbologyFromLayer_management(layer.name, layer_file)
        if zoom_to:
            df.extent = layer.getSelectedExtent()
        del mxd, df, layer

def AdoptParameter(provided_input, parameter_name, preserve_existing=True):
    """
    Copies the provided input into the geodatabase as the parameter_name
    parameter. If a feature class already exists with the parameter_name,
    a unique copy will be saved (with preserve_existing=True).
    Workspace must be defined as project's unique geodatabase before
    calling this function.
    :param provided_input: a feature class or shapefile
    :param parameter_name: the name to save the provided_input as string
    :param preserve_existing: True to avoid overwriting
    :return: the name of the adopted parameter as a string
    """
    # Save a copy of the existing feature class if it already exists
    if preserve_existing:
        if arcpy.Exists(parameter_name):
            new_parameter_name = arcpy.CreateUniqueName(parameter_name)
            arcpy.CopyFeatures_management(parameter_name, new_parameter_name)

    # Copy providedInput to temporary memory to allow overwriting
    arcpy.CopyFeatures_management(provided_input, "in_memory/tmp_provided")

    # Delete existing layers in the TOC of the paramaterName
    if arcpy.ListInstallations()[0] == 'arcgispro':
        p = arcpy.mp.ArcGISProject("CURRENT")
        m = p.activeMap
        for _ in m.listLayers():
            arcpy.Delete_management(parameter_name)
    else:
        mxd = arcpy.mapping.MapDocument("CURRENT")
        for _ in arcpy.mapping.ListLayers(mxd, parameter_name):
            arcpy.Delete_management(parameter_name)

    # Delete feature classes in the geodatabase
    for _ in arcpy.ListFeatureClasses(parameter_name):
        arcpy.Delete_management(parameter_name)

    # Execute renaming
    adopted_parameter = arcpy.CopyFeatures_management(
        "in_memory/tmp_provided", parameter_name
        )

    # Clean up
    arcpy.Delete_management("in_memory")

    return adopted_parameter
    
# FUNCTION CALLS
def generate_reports(map_units_dissolve, default_gdb, template_path, 
                    project_name, outputs, credit_report):
    '''saves the title page and map series in the outputs folder'''
    # Save map units as feature class in default gdb
    mu_save_name = os.path.join(default_gdb, 'Map_Units')
    mu_saved = AdoptParameter(map_units_dissolve, mu_save_name, 
                                preserve_existing=False)

    # Reset inset map
    mxd = arcpy.mapping.MapDocument("CURRENT")
    inset_map = arcpy.mapping.ListDataFrames(mxd)[1]
    inset_map.elementHeight = 2.5

    ## TITLE PAGE
    # Add map units dissole to map
    layer_file = os.path.join(template_path, 'Layer_Files', 'Map_Units.lyr')
    AddToMap(mu_saved, layer_file, zoom_to=True)

    # Update project title and 
    mxd.title = project_name  # map document property
    for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
        if elm.text == 'Project Name':
            elm.text = project_name

    # Export title page
    save_name = os.path.join(outputs, 'Credit_Summary_Report.pdf')
    arcpy.mapping.ExportToPDF(mxd, save_name)


    ## MAP SERIES INDEX PAGE
    # Create grid index
    grid_save_name = os.path.join(default_gdb, 'Grid')
    grid = arcpy.cartography.GridIndexFeatures(
        grid_save_name, mu_saved, "INTERSECTFEATURE", 
        "NO_USEPAGEUNIT", polygon_width=10000, polygon_height=10000
        )
    layer_file = os.path.join(template_path, 'Layer_Files', 'Grid_Reference.lyr')
    AddToMap(grid, layer_file, zoom_to=True)

    # Update title and summary text from overview layout
    for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"): 
        if elm.text == project_name: 
            elm.text = '{}: Grid Reference'.format(project_name)
        if elm.name == 'ProjectStats':
            elm.visible = False
        if elm.name == 'Header':
            elm.visible = False

    # create layer from grid
    grid_lyr = arcpy.mapping.ListLayers(mxd, 'Grid')[0]
        
    # Show labels
    grid_lyr.showLabels = True
    grid_lyr.expression = 'PageName'

    # Create destination PDF
    save_name = os.path.join(outputs, 'series.pdf')
    map_series = arcpy.mapping.PDFDocumentCreate(save_name)

    # Export grid index page and append to map_series
    save_name = os.path.join(outputs, 'grid_reference.pdf')
    arcpy.mapping.ExportToPDF(mxd, save_name)
    map_series.appendPages(save_name)
    os.remove(save_name)


    ## MAP SERIES
    df = mxd.activeDataFrame

    # create layer file from map units
    mu_base_name = arcpy.Describe(mu_saved).baseName
    mu_lyr = arcpy.mapping.ListLayers(mxd, mu_base_name)[0]

    # read in attribute data for symbolization
    credit_report = credit_report[['map_unit_id', 'saleable_credits']]
    credit_report['saleable_credits'] = credit_report['saleable_credits'].fillna(0)
    credit_report['saleable_credits'] = credit_report['saleable_credits'].round(2)
    credit_report.columns = ['mu_id', 'display']  # to avoid truncation in shapefiles
    values_array = np.array(np.rec.fromrecords(credit_report.values))
    names = credit_report.dtypes.index.tolist()
    values_array.dtype.names = tuple(names)
    table_name = os.path.join(default_gdb, 'values_table')
    if arcpy.Exists(table_name):
        arcpy.Delete_management(table_name)
    arcpy.da.NumPyArrayToTable(values_array, table_name)

    # get map unit id field (may be truncated in shapefiles)
    mu_id_field = arcpy.ListFields(mu_lyr, 'Map_Unit_I*')[0].name

    existingFields = arcpy.ListFields(mu_lyr)
    fieldNames = [field.name.lower() for field in existingFields]
    if 'display' in fieldNames:
        arcpy.DeleteField_management(mu_lyr, 'display')

    arcpy.JoinField_management(mu_lyr, mu_id_field, 
                                table_name, 'mu_id')

    # Symbolize grid and turn off labels
    layer_file = os.path.join(template_path, 'Layer_Files', 'Grid_Zoom.lyr')
    arcpy.ApplySymbologyFromLayer_management(grid_lyr, layer_file)
    grid_lyr.showLabels = False

    # Symbolize map unit layers
    layer_file = os.path.join(template_path, 'Layer_Files', 'Map_Units_Zoom.lyr')
    arcpy.ApplySymbologyFromLayer_management(mu_lyr, layer_file)
    sym = mu_lyr.symbology
    old_labels = sym.classBreakLabels
    new_labels = []
    for label_range in old_labels:
        start_label = label_range.split(' - ')[0]
        start_label = round(float(start_label), 2)
        end_label = label_range.split(' - ')[1]
        end_label = round(float(end_label), 2)
        class_labels = '{0} - {1}'.format(start_label, end_label)
        new_labels.append(class_labels)
    sym.classBreakLabels = new_labels

    # update map unit labels
    for label in mu_lyr.labelClasses:
        label.expression = '[{}]'.format(mu_id_field)
    mu_lyr.showLabels = True

    # for each page number in output_grid:
    with arcpy.da.SearchCursor(grid, ['PageNumber', 'PageName']) as cursor:
        previous_page_name = ''
        for row in cursor:
            arcpy.AddMessage('Saving Map Series page {}'.format(row[1]))
            # zoom to grid
            where_clause = '"PageNumber" = {}'.format(row[0])
            arcpy.SelectLayerByAttribute_management(
                grid_lyr, where_clause=where_clause
                )
            df.zoomToSelectedFeatures()
            arcpy.RefreshActiveView
            arcpy.SelectLayerByAttribute_management(grid_lyr, 'CLEAR_SELECTION')
        
            # update title with reference
            new_text = '{}: {}'.format(project_name, row[1])
            for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
                if (elm.text == '{}: Grid Reference'.format(project_name) 
                    or elm.text == previous_page_name):
                    elm.text = new_text
                    previous_page_name = new_text

            # replace inset map with legend by removing inset
            inset_map.elementHeight = 0
            
            # export view to pdf
            save_name = os.path.join(outputs, 'grid_page.pdf')
            arcpy.mapping.ExportToPDF(mxd, save_name)
            map_series.appendPages(save_name)    
            os.remove(save_name)

    # Save map document
    mxd.save()