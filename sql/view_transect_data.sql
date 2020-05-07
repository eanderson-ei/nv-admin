CREATE VIEW IF NOT EXISTS view_transect_data AS-- begin shrub data
WITH shrub AS (
        SELECT transect_id,
               sum(shrub_end - shrub_start) / 50 AS shrub_cover
          FROM shrub_data
         GROUP BY transect_id
    ),
    sage AS (
        SELECT transect_id,
               sum(shrub_end - shrub_start) / 50 AS sage_cover,
               avg(shrub_height) AS sage_height
          FROM shrub_data
         WHERE shrub_type != 'Other'
         GROUP BY transect_id
    ),
    sage_shrub AS (
        SELECT shrub.transect_id,
               shrub.shrub_cover,
               sage.sage_cover,
               sage.sage_height
          FROM shrub
               LEFT JOIN
               sage ON shrub.transect_id = sage.transect_id
    ),-- Note transects present in field info will be present in final table
    shrubs_by_transect AS (
        SELECT field_info.map_unit_id,
               field_info.map_unit_name,
               field_info.transect_id,
               field_info.meadow,
               field_info.sage_species,
               field_info.dist_sage,
               sage_shrub.sage_cover,
               sage_shrub.sage_height,
               sage_shrub.shrub_cover
          FROM field_info
               LEFT JOIN
               sage_shrub ON field_info.transect_id = sage_shrub.transect_id
    ),-- Begin forb and grass data
    melted AS (
        SELECT map_unit_id,
               transect_id,
               plot_id,
               'forb' AS attribute,
               forb_class AS cover_class
          FROM plot_data
        UNION ALL
        SELECT map_unit_id,
               transect_id,
               plot_id,
               'grass' AS attribute,
               grass_class
          FROM plot_data
        UNION ALL
        SELECT map_unit_id,
               transect_id,
               plot_id,
               'brotec' AS attribute,
               brotec_class
          FROM plot_data
    ),
    melted_cover AS (
        SELECT melted.map_unit_id,
               melted.transect_id,
               melted.plot_id,
               melted.attribute,
               melted.cover_class,
               cover_classes.cover AS pct_cover
          FROM melted
               LEFT JOIN
               cover_classes ON melted.cover_class = cover_classes.class
    ),
    plot_cover AS (
        SELECT melted_cover.map_unit_id,
               melted_cover.transect_id,
               melted_cover.attribute,
               AVG(melted_cover.pct_cover) AS pct_cover
          FROM melted_cover
         GROUP BY melted_cover.transect_id,
                  melted_cover.attribute
    ),
    grasses_forbs_by_transect AS (
        SELECT forb_grass_data.map_unit_id,
               forb_grass_data.transect_id,
               AVG(CASE WHEN plot_cover.transect_id = forb_grass_data.transect_id AND 
                             plot_cover.attribute = 'forb' THEN plot_cover.pct_cover END) AS forb_cover,
               forb_grass_data.unique_forbs,
               AVG(CASE WHEN plot_cover.transect_id = forb_grass_data.transect_id AND 
                             plot_cover.attribute = 'grass' THEN plot_cover.pct_cover END) AS grass_cover,
               AVG(CASE WHEN plot_cover.transect_id = forb_grass_data.transect_id AND 
                             plot_cover.attribute = 'brotec' THEN plot_cover.pct_cover END) AS brotec_cover
          FROM forb_grass_data
               LEFT JOIN
               plot_cover ON forb_grass_data.transect_id = plot_cover.transect_id
         GROUP BY forb_grass_data.transect_id
    )-- combine shrubs with forbs and grasses
    SELECT s.map_unit_id,
           s.map_unit_name,
           s.transect_id,
           s.meadow,
           s.sage_species,
           s.dist_sage,
           s.sage_cover,
           s.sage_height,
           s.shrub_cover,
           f.forb_cover,
           f.unique_forbs,
           f.grass_cover,
           f.brotec_cover
      FROM shrubs_by_transect AS s
           LEFT JOIN
           grasses_forbs_by_transect AS f ON s.transect_id = f.transect_id;
