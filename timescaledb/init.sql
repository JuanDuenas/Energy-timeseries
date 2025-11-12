CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS measurements (
    id SERIAL PRIMARY KEY,
    sensor_id INT,
    timestamp TIMESTAMPTZ NOT NULL,
    value DOUBLE PRECISION,
    type VARCHAR(20),
    location VARCHAR(100)
);

SELECT create_hypertable('measurements', 'timestamp', if_not_exists => TRUE);

-- Índices útiles para consultas de tendencia
CREATE INDEX IF NOT EXISTS idx_measurements_time ON measurements (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_measurements_type ON measurements (type);
