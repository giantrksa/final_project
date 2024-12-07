-- dags/init_postgres.sql

CREATE TABLE IF NOT EXISTS las_data (
    id SERIAL PRIMARY KEY,
    DEPT FLOAT,
    DT FLOAT,
    RHOB FLOAT,
    NPHI FLOAT,
    GR FLOAT
    -- Add other LAS curve columns as needed
);
