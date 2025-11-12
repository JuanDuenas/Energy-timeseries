from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables del entorno (.env)
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "energia_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Crea la tabla y la convierte en hypertable si no existe."""
    with engine.connect() as conn:
        # Extensión TimescaleDB
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))

        # Crear tabla
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS measurements (
                id SERIAL,
                sensor_id INT,
                timestamp TIMESTAMPTZ NOT NULL,
                value DOUBLE PRECISION,
                type VARCHAR(50),
                location VARCHAR(100),
                PRIMARY KEY (id, timestamp)
            );
        """))

        # Crear hypertable si no existe
        conn.execute(text("""
            SELECT create_hypertable('measurements', 'timestamp', if_not_exists => TRUE);
        """))

        conn.commit()
