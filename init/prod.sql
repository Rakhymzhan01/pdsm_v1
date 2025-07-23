-- Table: prod
DROP TABLE IF EXISTS prod;
CREATE TABLE prod (
    "Date" date,
    "Well" text,
    "Horizon" text,
    "Pump" double precision,
    "H_m" double precision,
    "Ptr_atm" double precision,
    "Pztr_atm" double precision,
    "Time_hr" double precision,
    "Ql_m3" double precision,
    "Qo_m3" double precision,
    "Qw_m3" double precision,
    "Qo_ton" double precision,
    "Qi_m3" double precision
);

\COPY prod FROM '/docker-entrypoint-initdb.d/prod.csv' DELIMITER ',' CSV HEADER;
