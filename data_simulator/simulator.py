import time
import random
import requests
import datetime
from config import API_URL, INTERVAL

SENSORS = [
    {"id": 1, "type": "solar", "location": "Planta Solar Norte"},
    {"id": 2, "type": "solar", "location": "Planta Solar Sur"},
    {"id": 3, "type": "eolica", "location": "Parque Eólico Este"},
    {"id": 4, "type": "eolica", "location": "Parque Eólico Oeste"},
]

def generate_measurement(sensor):
    """Genera un valor simulado de potencia para cada sensor."""
    if sensor["type"] == "solar":
        value = round(random.uniform(100, 1000), 2)
    else:
        value = round(random.uniform(200, 1200), 2)

    return {
        "sensor_id": sensor["id"],
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "value": value,
        "type": sensor["type"],
        "location": sensor["location"]
    }

def send_data(data):
    """Envía la medición a la API."""
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            print(f"✅ Dato enviado: {data}")
        else:
            print(f"⚠️ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error al conectar con API: {e}")

def main():
    print("🚀 Iniciando simulador de datos de energía renovable...")
    while True:
        for sensor in SENSORS:
            measurement = generate_measurement(sensor)
            send_data(measurement)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
