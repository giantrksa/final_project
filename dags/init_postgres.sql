-- dags/init_postgres.sql

CREATE TABLE IF NOT EXISTS las_data (
    DEPT FLOAT,
    DT FLOAT,
    RHOB FLOAT,
    NPHI FLOAT,
    GR FLOAT
    -- Add other fields as necessary
);
