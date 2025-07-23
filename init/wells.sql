-- Table: wells
DROP TABLE IF EXISTS wells;
CREATE TABLE wells (
    "Well" text,
    "X" text,
    "Y" text,
    "Lat" text,
    "Lon" text,
    "Object" text,
    "Year" text
);

\COPY wells FROM '/docker-entrypoint-initdb.d/wells.csv' DELIMITER ',' CSV HEADER;
