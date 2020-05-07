CREATE TABLE IF NOT EXISTS transect_review (
    map_unit_id integer,
    map_unit_name text,
    transect_id integer,
    evaluated text,
    meadow text,
    sage_species text,
    dist_sage real,
    sage_cover real,
    sage_height real,
    shrub_cover real,
    forb_cover real,
    forb_rich real,
    grass_cover real,
    brotec_cover real
);