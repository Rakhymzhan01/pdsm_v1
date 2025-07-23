-- Table: pvt
DROP TABLE IF EXISTS pvt;
CREATE TABLE pvt (
    "Скважина" text,
    "Дата отбора" text,
    "Точка отбора" text,
    "Сервисная компания" text,
    "Лаборатория" text,
    "Интервал отбора" text,
    "Горизонт" text,
    "Давление (атм)" double precision,
    "Температура (С)" double precision,
    "Давление насыщения (атм)" double precision,
    "Газовый фактор (м3/т)" double precision,
    "Плотность нефти (г/cм3)" double precision,
    "Объемный коэффициент (Во)" double precision,
    "Вязкость (сП)" double precision
);

\COPY pvt FROM '/docker-entrypoint-initdb.d/pvt.csv' DELIMITER ',' CSV HEADER;
