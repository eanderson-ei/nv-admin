CREATE VIEW IF NOT EXISTS view_reserve_account AS
WITH base_contribution AS (
        SELECT b.map_unit_id,
               s.standard_value AS base_contribution
          FROM baseline_rr_inputs AS b
               LEFT JOIN
               standard_values AS s
         WHERE s.variable = 'standard_contribution'
    ),
    rr_rating AS (
        SELECT i.map_unit_id,
               i.rr_score,
               r.category AS rr_rating
          FROM baseline_rr_inputs AS i
               LEFT JOIN
               rr_scores AS r ON i.rr_score >= r.score
         GROUP BY i.map_unit_id
        HAVING max(r.score) 
    ),
    wildfire_rating AS (
        SELECT i.map_unit_id,
               i.wildfire_score,
               w.category AS wildfire_rating
          FROM baseline_rr_inputs AS i
               LEFT JOIN
               wildfire_scores AS w ON i.wildfire_score >= w.score
         GROUP BY i.map_unit_id
        HAVING max(w.score) 
    ),
    combined_rating AS (
        SELECT rr_rating.map_unit_id,
               rr_rating.rr_rating,
               wildfire_rating.wildfire_rating
          FROM rr_rating
               LEFT JOIN
               wildfire_rating ON rr_rating.map_unit_id = wildfire_rating.map_unit_id
    )
    SELECT b.map_unit_id,
           b.base_contribution,
           c.rr_rating,
           c.wildfire_rating,
           rr.contribution AS wildfire_contribution,
           i.land_use_contribution,
           (b.base_contribution + rr.contribution + i.land_use_contribution) AS total_contribution
      FROM base_contribution AS b
           LEFT JOIN
           combined_rating AS c ON b.map_unit_id = c.map_unit_id
           LEFT JOIN
           rr_add_contribution AS rr ON c.rr_rating = rr.rr AND 
                                        c.wildfire_rating = rr.wildfire
           LEFT JOIN
           baseline_rr_inputs AS i ON b.map_unit_id = i.map_unit_id;
