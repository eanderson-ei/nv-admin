CREATE TABLE IF NOT EXISTS transect_data (
    transect_id integer,
    utm_e real,
    utm_n real,
    bearing1 integer,
    bearing2 integer,
    bearing3 integer,
    sample_type text,
    notes text,
    map_unit_id integer
);