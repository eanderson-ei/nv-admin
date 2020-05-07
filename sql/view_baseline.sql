CREATE VIEW IF NOT EXISTS view_baseline AS
WITH weighted_baseline AS (
        SELECT d.map_unit_id,
               d.indirect_benefits_area,
               d.mz3,
               d.mz4,
               d.mz5,
               b.season,
               SUM(CASE WHEN b.mgmt_zone = 'MZ III' THEN d.mz3 * b.baseline END) AS mz3_weighted,
               SUM(CASE WHEN b.mgmt_zone = 'MZ IV' THEN d.mz4 * b.baseline END) AS mz4_weighted,
               SUM(CASE WHEN b.mgmt_zone = 'MZ V' THEN d.mz5 * b.baseline END) AS mz5_weighted
          FROM view_desktop_results AS d
               LEFT JOIN
               standard_baseline AS b
         GROUP BY d.map_unit_id,
                  b.season
    )
    SELECT map_unit_id,
           season,
           (mz3_weighted + mz4_weighted + mz5_weighted) AS baseline
      FROM weighted_baseline;
