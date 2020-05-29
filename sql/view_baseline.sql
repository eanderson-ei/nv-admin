CREATE VIEW IF NOT EXISTS view_baseline AS
    SELECT d.map_unit_id,
           b.season,
           (SUM(CASE WHEN b.mgmt_zone = 'MZ III' THEN d.mz3 * b.baseline END) + SUM(CASE WHEN b.mgmt_zone = 'MZ IV' THEN d.mz4 * b.baseline END) + SUM(CASE WHEN b.mgmt_zone = 'MZ V' THEN d.mz5 * b.baseline END) ) AS baseline
      FROM view_desktop_results AS d
           LEFT JOIN
           standard_baseline AS b
     GROUP BY d.map_unit_id,
              b.season;
