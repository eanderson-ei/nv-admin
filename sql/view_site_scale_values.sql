CREATE VIEW IF NOT EXISTS view_site_scale_values AS
WITH count_sage_species AS (
        SELECT map_unit_id,
               sage_species,
               COUNT(sage_species) AS dominant_species
          FROM view_transect_data
         GROUP BY map_unit_id,
                  sage_species
         ORDER BY map_unit_id
    ),
    dominant_sage_species AS (
        SELECT map_unit_id,
               sage_species
          FROM count_sage_species
         GROUP BY map_unit_id
        HAVING MAX(dominant_species) 
    ),
    map_unit_less_sage_species AS (
        SELECT map_unit_id,
               map_unit_name,
               COUNT(transect_id) AS no_transects,
               meadow,
               SUM(dist_sage)/COUNT(transect_id) AS dist_sage,
               SUM(sage_cover)/COUNT(transect_id) AS sage_cover,
               SUM(sage_height)/COUNT(transect_id) AS sage_height,
               SUM(shrub_cover)/COUNT(transect_id) AS shrub_cover,
               SUM(forb_cover)/COUNT(transect_id) AS forb_cover,
               SUM(unique_forbs)/COUNT(transect_id) AS forb_rich,
               SUM(grass_cover)/COUNT(transect_id) AS grass_cover,
               SUM(brotec_cover)/COUNT(transect_id) AS brotec_cover
          FROM view_transect_data
         GROUP BY map_unit_id
    )
    SELECT m.map_unit_id,
           m.map_unit_name,
           r.map_unit_area,
           r.indirect_benefits_area,
           m.no_transects,
           m.meadow,
           r.arid,
           r.mesic,
           r.conifer_phase,
           r.spring_hsi,
           r.summer_hsi,
           r.winter_hsi,
           d.sage_species,
           m.dist_sage,
           m.sage_cover,
           m.sage_height,
           m.shrub_cover,
           m.forb_cover,
           m.forb_rich,
           m.grass_cover,
           m.brotec_cover
      FROM map_unit_less_sage_species AS m
           LEFT JOIN
           dominant_sage_species AS d ON m.map_unit_id = d.map_unit_id
           LEFT JOIN
           view_desktop_results AS r on m.map_unit_id = r.map_unit_id;
