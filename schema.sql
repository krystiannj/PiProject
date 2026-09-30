CREATE TABLE system_stats (
    id SERIAL PRIMARY KEY,
    container_name VARCHAR(100),
    timestamp TIMESTAMPTZ,
    cpu_usage DOUBLE PRECISION,
    memory_usage DOUBLE PRECISION,
    cpu_temperature DOUBLE PRECISION,
    status VARCHAR(20),
    swap_usage DOUBLE PRECISION,
    storage_usage DOUBLE PRECISION,
    storage_free DOUBLE PRECISION,
    storage_total DOUBLE PRECISION,
    storage_used DOUBLE PRECISION
);

CREATE TABLE honeypot_logs (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(50),
    timestamp TIMESTAMPTZ
);
