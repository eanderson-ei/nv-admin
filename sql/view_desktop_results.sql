CREATE VIEW IF NOT EXISTS view_desktop_results AS
    SELECT m.map_unit_id,
           m.map_unit_name,
           m.meadow,
           (CASE WHEN m.conifer_phase IS NULL THEN 'None' END) AS conifer_phase,
           m.indirect_benefits_area,
           m.map_unit_area,
           m.no_transects,
           m.spring_hsi,
           m.summer_hsi,
           m.winter_hsi,
           cl.ls_breed AS current_breed,
           cl.ls_summer AS current_summer,
           cl.ls_winter AS current_winter,
           pl.ls_breed AS projected_breed,
           pl.ls_summer AS projected_summer,
           pl.ls_winter AS projected_winter,
           (
               SELECT (CASE WHEN mgmt_cat = 'PHMA' THEN proportion ELSE 0 END) 
                 FROM project_mgmt_cats
                WHERE project_mgmt_cats.map_unit_id = m.map_unit_id
           )
           AS phma,
           (
               SELECT (CASE WHEN mgmt_cat = 'GHMA' THEN proportion ELSE 0 END) 
                 FROM project_mgmt_cats
                WHERE project_mgmt_cats.map_unit_id = m.map_unit_id
           )
           AS ghma,
           (
               SELECT (CASE WHEN mgmt_cat = 'OHMA' THEN proportion ELSE 0 END) 
                 FROM project_mgmt_cats
                WHERE project_mgmt_cats.map_unit_id = m.map_unit_id
           )
           AS ohma,
           (
               SELECT (CASE WHEN wmz = 'MZ III' THEN proportion ELSE 0 END) 
                 FROM project_wmz
                WHERE project_wmz.map_unit_id = m.map_unit_id
           )
           AS mz3,
           (
               SELECT (CASE WHEN wmz = 'MZ IV' THEN proportion ELSE 0 END) 
                 FROM project_wmz
                WHERE project_wmz.map_unit_id = m.map_unit_id
           )
           AS mz4,
           (
               SELECT (CASE WHEN wmz = 'MZ V' THEN proportion ELSE 0 END) 
                 FROM project_wmz
                WHERE project_wmz.map_unit_id = m.map_unit_id
           )
           AS mz5,
           (
               SELECT (CASE WHEN precip = 'Arid' THEN proportion ELSE 0 END) 
                 FROM project_precip
                WHERE project_precip.map_unit_id = m.map_unit_id
           )
           AS arid,
           (
               SELECT (CASE WHEN precip = 'Mesic' THEN proportion ELSE 0 END) 
                 FROM project_precip
                WHERE project_precip.map_unit_id = m.map_unit_id
           )
           AS mesic
      FROM map_units AS m
           LEFT JOIN
           current_ls AS cl ON m.map_unit_id = cl.map_unit_id
           LEFT JOIN
           projected_ls AS pl ON m.map_unit_id = pl.map_unit_id;
