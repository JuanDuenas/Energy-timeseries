from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from database import engine, SessionLocal, init_db
from models import Measurement

app = FastAPI(title="API de Energía Renovable")
init_db()

@app.post("/data")
def insert_data(data: Measurement):
    """Recibe una medición y la inserta en la base de datos."""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO measurements (sensor_id, timestamp, value, type, location)
                VALUES (:sensor_id, :timestamp, :value, :type, :location)
            """), data.dict())
            conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/latest")
def get_latest(limit: int = 10):
    """Devuelve las últimas mediciones."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM measurements
            ORDER BY timestamp DESC
            LIMIT :limit
        """), {"limit": limit})
        return [dict(row) for row in result]

@app.get("/data/average")
def get_average():
    """Ejemplo de consulta agregada: promedio por tipo."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT type, AVG(value) AS avg_value
            FROM measurements
            GROUP BY type;
        """))
        return [dict(row) for row in result]
