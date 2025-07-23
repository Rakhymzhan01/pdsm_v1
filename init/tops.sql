-- Table: tops
DROP TABLE IF EXISTS tops;
CREATE TABLE tops (
    "well" text,
    "XII_a" text,
    "XI_1_Br" text,
    "XI_br" text,
    "X_Br" text,
    "IX Br" text,
    "VIII_K1b" text,
    "VII g(J2-?)" text,
    "J2_IIIa" text,
    "V_J" text,
    "V_J2_b" text,
    "V-1" text,
    "V2_J2" text,
    "V3_J2" text,
    "V3_b" text,
    "J1-IV-2" text,
    "J1-IV-1" text,
    "T_BJ(base_IV-1)" text,
    "T Upper Part" double precision,
    "T-II" text,
    "Top_P2(I-P)" text,
    "P1k_anh" text,
    "P1k_gal" double precision
);

\COPY tops FROM '/docker-entrypoint-initdb.d/tops.csv' DELIMITER ',' CSV HEADER;
