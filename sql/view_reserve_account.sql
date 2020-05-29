CREATE VIEW IF NOT EXISTS view_reserve_account AS
    SELECT b.map_unit_id,
           (
               SELECT s.standard_value
                 FROM standard_values AS s
                WHERE s.variable = 'standard_contribution'
           )
           AS base_contribution,
           (
               SELECT r.category
                 FROM baseline_rr_inputs AS i
                      LEFT JOIN
                      rr_scores AS r ON i.rr_score >= r.score
                GROUP BY i.map_unit_id
               HAVING max(r.score) 
           )
           AS rr_rating,
           (
               SELECT w.category
                 FROM baseline_rr_inputs AS i
                      LEFT JOIN
                      wildfire_scores AS w ON i.wildfire_score >= w.score
                GROUP BY i.map_unit_id
               HAVING max(w.score) 
           )
           AS wildfire_rating,
           rr.contribution AS wildfire_contribution,
           i.land_use_contribution,
           ( (
                 SELECT s.standard_value
                   FROM standard_values AS s
                  WHERE s.variable = 'standard_contribution'
             ) 
             + rr.contribution + i.land_use_contribution) AS total_contribution
      FROM baseline_rr_inputs AS b
           LEFT JOIN
           rr_add_contribution AS rr ON rr_rating = rr.rr AND 
                                        wildfire_rating = rr.wildfire
           LEFT JOIN
           baseline_rr_inputs AS i ON b.map_unit_id = i.map_unit_id;
