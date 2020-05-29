CREATE VIEW IF NOT EXISTS view_transect_data AS
    SELECT field_info.map_unit_id,
           field_info.map_unit_name,
           field_info.transect_id,
           field_info.meadow,
           field_info.sage_species,
           field_info.dist_sage,
           (
               SELECT sum(shrub_end - shrub_start) / 50
                 FROM shrub_data
                WHERE shrub_type != 'Other' AND 
                      shrub_data.transect_id = field_info.transect_id
                GROUP BY transect_id
           )
           AS sage_cover,
           (
               SELECT avg(shrub_height) AS sage_height
                 FROM shrub_data
                WHERE shrub_type != 'Other' AND 
                      shrub_data.transect_id = field_info.transect_id
                GROUP BY transect_id
           )
           AS sage_height,
           (
               SELECT sum(shrub_end - shrub_start) / 50
                 FROM shrub_data
                WHERE shrub_data.transect_id = field_info.transect_id
                GROUP BY transect_id
           )
           AS shrub_cover,
           (
               SELECT AVG(pct_cover) 
                 FROM (
                          SELECT transect_id,
                                 cover_classes.cover AS pct_cover
                            FROM plot_data
                                 LEFT JOIN
                                 cover_classes ON plot_data.forb_class = cover_classes.class
                      )
                WHERE field_info.transect_id = transect_id
                GROUP BY transect_id
           )
           AS forb_cover,
           (
               SELECT unique_forbs
                 FROM forb_grass_data
                WHERE field_info.transect_id = forb_grass_data.transect_id
           )
           AS unique_forbs,
           (
               SELECT AVG(pct_cover) 
                 FROM (
                          SELECT transect_id,
                                 cover_classes.cover AS pct_cover
                            FROM plot_data
                                 LEFT JOIN
                                 cover_classes ON plot_data.grass_class = cover_classes.class
                      )
                WHERE field_info.transect_id = transect_id
                GROUP BY transect_id
           )
           AS grass_cover,
           (
               SELECT AVG(pct_cover) 
                 FROM (
                          SELECT transect_id,
                                 cover_classes.cover AS pct_cover
                            FROM plot_data
                                 LEFT JOIN
                                 cover_classes ON plot_data.brotec_class = cover_classes.class
                      )
                WHERE field_info.transect_id = transect_id
                GROUP BY transect_id
           )
           AS brotec_cover
      FROM field_info;
