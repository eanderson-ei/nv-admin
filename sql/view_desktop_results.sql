CREATE VIEW IF NOT EXISTS view_desktop_results AS
WITH precip_unstack AS (
        SELECT map_unit_id,
               (CASE WHEN precip = 'Arid' THEN proportion ELSE 0 END) AS arid,
               (CASE WHEN precip = 'Mesic' THEN proportion ELSE 0 END) AS mesic
          FROM project_precip
    ),
    mgmt_cat_unstack AS (
        SELECT map_unit_id,
               (CASE WHEN mgmt_cat = 'PHMA' THEN proportion ELSE 0 END) AS phma,
               (CASE WHEN mgmt_cat = 'GHMA' THEN proportion ELSE 0 END) AS ghma,
               (CASE WHEN mgmt_cat = 'OHMA' THEN proportion ELSE 0 END) AS ohma
          FROM project_mgmt_cats
    ),
    wmz_unstack AS (
        SELECT map_unit_id,
               (CASE WHEN wmz = 'MZ III' THEN proportion ELSE 0 END) AS mz3,
               (CASE WHEN wmz = 'MZ IV' THEN proportion ELSE 0 END) AS mz4,
               (CASE WHEN wmz = 'MZ V' THEN proportion ELSE 0 END) AS mz5
          FROM project_wmz
    )
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
           cl.ls_breed as current_breed,
           cl.ls_summer as current_summer,
           cl.ls_winter as current_winter,
           pl.ls_breed as projected_breed,
           pl.ls_summer as projected_summer,
           pl.ls_winter as projected_winter,
           mgmt.phma,
           mgmt.ghma,
           mgmt.ohma,
           wmz.mz3,
           wmz.mz4,
           wmz.mz5,
           precip.arid,
           precip.mesic
      FROM map_units AS m
           LEFT JOIN
           current_ls AS cl ON m.map_unit_id = cl.map_unit_id
           LEFT JOIN
           projected_ls AS pl ON m.map_unit_id = pl.map_unit_id
           LEFT JOIN
           mgmt_cat_unstack AS mgmt ON m.map_unit_id = mgmt.map_unit_id
           LEFT JOIN
           wmz_unstack AS wmz ON m.map_unit_id = wmz.map_unit_id
           LEFT JOIN
           precip_unstack AS precip ON m.map_unit_id = precip.map_unit_id;
