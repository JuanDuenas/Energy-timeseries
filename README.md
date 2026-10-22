# Energy-timeseries

Sistema de monitoreo de energía renovable en tiempo real basado en microservicios. Simula sensores de plantas solares y parques eólicos, almacena las mediciones en **TimescaleDB** (PostgreSQL optimizado para series de tiempo) y las visualiza mediante dashboards en **Grafana**, todo orquestado con **Docker Compose**.

---

## Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Puesta en Marcha](#instalación-y-puesta-en-marcha)
- [Servicios y Puertos](#servicios-y-puertos)
- [API REST](#api-rest)
- [Simulador de Datos](#simulador-de-datos)
- [Base de Datos](#base-de-datos)
- [Grafana y Dashboards](#grafana-y-dashboards)
- [Variables de Entorno](#variables-de-entorno)
- [Backups](#backups)

---

## Arquitectura

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  data_simulator │──POST──▶│   API (FastAPI)   │──SQL───▶│  TimescaleDB     │
│  (sensores)     │         │  :8000 → :5000   │         │  (PostgreSQL 16) │
└─────────────────┘         └──────────────────┘         └────────┬─────────┘
                                                                   │
                                                          ┌────────▼─────────┐
                                                          │     Grafana       │
                                                          │  Dashboards :3000 │
                                                          └──────────────────┘
```

Todos los servicios se comunican dentro de la red Docker interna `energia_net`.

---

## Tecnologías

| Componente       | Tecnología                          | Versión        |
|------------------|--------------------------------------|----------------|
| API REST         | FastAPI + Uvicorn                   | Python 3.11    |
| ORM / DB Driver  | SQLAlchemy + psycopg2               | —              |
| Validación       | Pydantic                            | —              |
| Base de Datos    | TimescaleDB sobre PostgreSQL        | latest-pg16    |
| Visualización    | Grafana                             | (build propio) |
| Simulador        | Python (requests + random)          | Python 3.11    |
| Orquestación     | Docker Compose                      | —              |

---

## Estructura del Proyecto

```
Energy-timeseries/
│
├── docker-compose.yml          # Orquestación de todos los servicios
│
├── api/                        # Servicio API REST (FastAPI)
│   ├── Dockerfile
│   ├── main.py                 # Endpoints REST
│   ├── database.py             # Conexión y creación de hypertable
│   ├── models.py               # Modelo Pydantic Measurement
│   └── requirements.txt
│
├── data_simulator/             # Simulador de sensores
│   ├── Dockerfile
│   ├── simulator.py            # Loop de generación y envío de datos
│   ├── config.py               # Configuración vía variables de entorno
│   └── requirements.txt
│
├── timescaledb/                # Base de datos
│   ├── Dockerfile
│   └── init.sql                # Inicialización de tablas e índices
│
├── grafana/                    # Visualización
│   ├── Dockerfile
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml        # Conexión a TimescaleDB
│       └── dashboards/
│           ├── dashboards.yml        # Proveedor de dashboards
│           └── energia_dashboard.json # Dashboard preconfigurado
│
└── backups/
    └── energia_db.sql          # Backup de la base de datos
```

---

## Requisitos Previos

- [Docker](https://www.docker.com/) >= 20.x
- [Docker Compose](https://docs.docker.com/compose/) (incluido en Docker Desktop)
- Puertos libres: `3000`, `5000`, `5432`

---

## Instalación y Puesta en Marcha

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/Energy-timeseries.git
cd Energy-timeseries
```

### 2. Levantar todos los servicios

```bash
docker compose up --build
```

> La primera vez construirá todas las imágenes. Las sucesivas levantarán los contenedores sin reconstruir.

### 3. Verificar que todos los servicios están corriendo

```bash
docker compose ps
```

### 4. Acceder a los servicios

| Servicio    | URL                                   |
|-------------|---------------------------------------|
| API Docs    | http://localhost:5000/docs            |
| Grafana     | http://localhost:3000                 |
| TimescaleDB | `localhost:5432` (cliente PostgreSQL) |

### 5. Detener los servicios

```bash
docker compose down
```

Para eliminar también los volúmenes (datos de BD):

```bash
docker compose down -v
```

---

## Servicios y Puertos

| Servicio         | Puerto Interno | Puerto Expuesto | Descripción                           |
|------------------|----------------|-----------------|---------------------------------------|
| `timescaledb`    | 5432           | 5432            | Base de datos TimescaleDB/PostgreSQL  |
| `api`            | 8000           | 5000            | API REST FastAPI                      |
| `data_simulator` | —              | —               | Servicio interno, sin puerto expuesto |
| `grafana`        | 3000           | 3000            | Dashboard de visualización            |

---

## API REST

La API está construida con **FastAPI** y expone los siguientes endpoints:

### `POST /data`

Inserta una nueva medición de sensor en la base de datos.

**Body (JSON):**
```json
{
  "sensor_id": 1,
  "timestamp": "2026-10-22T18:00:00Z",
  "value": 850.5,
  "type": "solar",
  "location": "Planta Solar Norte"
}
```

**Respuesta exitosa:**
```json
{ "status": "success" }
```

---

### `GET /data/latest?limit=10`

Retorna las últimas N mediciones ordenadas por timestamp descendente.

**Parámetros:**

| Parámetro | Tipo | Default | Descripción                |
|-----------|------|---------|----------------------------|
| `limit`   | int  | `10`    | Número máximo de registros |

**Respuesta:**
```json
[
  {
    "id": 42,
    "sensor_id": 3,
    "timestamp": "2026-10-22T18:00:05Z",
    "value": 765.2,
    "type": "eolica",
    "location": "Parque Eólico Este"
  }
]
```

---

### `GET /data/average`

Retorna el promedio de potencia agrupado por tipo de energía.

**Respuesta:**
```json
[
  { "type": "solar", "avg_value": 550.34 },
  { "type": "eolica", "avg_value": 700.12 }
]
```

Documentación interactiva disponible en: **http://localhost:5000/docs** (Swagger UI)

---

## Simulador de Datos

El servicio `data_simulator` simula **4 sensores** de energía renovable que envían lecturas periódicas a la API:

| Sensor ID | Tipo   | Ubicación           | Rango de Valores |
|-----------|--------|---------------------|------------------|
| 1         | solar  | Planta Solar Norte  | 100 – 1000 kW    |
| 2         | solar  | Planta Solar Sur    | 100 – 1000 kW    |
| 3         | eólica | Parque Eólico Este  | 200 – 1200 kW    |
| 4         | eólica | Parque Eólico Oeste | 200 – 1200 kW    |

- **Intervalo de envío:** cada `5` segundos (configurable vía `INTERVAL`)
- **Endpoint destino:** `http://api:8000/data` (interno Docker)
- Los valores se generan con `random.uniform()` para simular variabilidad real

---

## Base de Datos

**TimescaleDB** extiende PostgreSQL con optimizaciones nativas para series temporales mediante el concepto de **hypertable**.

### Tabla `measurements`

| Columna     | Tipo             | Descripción                           |
|-------------|------------------|---------------------------------------|
| `id`        | SERIAL           | Identificador autoincremental         |
| `sensor_id` | INT              | ID del sensor origen                  |
| `timestamp` | TIMESTAMPTZ      | Marca de tiempo con zona horaria      |
| `value`     | DOUBLE PRECISION | Potencia registrada (kW)              |
| `type`      | VARCHAR(20)      | Tipo de energía (`solar` / `eolica`)  |
| `location`  | VARCHAR(100)     | Ubicación física del sensor           |

### Índices

```sql
-- Consultas de tendencia temporal
CREATE INDEX idx_measurements_time ON measurements (timestamp DESC);

-- Filtrado por tipo de energía
CREATE INDEX idx_measurements_type ON measurements (type);
```

### Hypertable

La tabla es convertida automáticamente en una **hypertable** de TimescaleDB particionada por `timestamp`, lo que permite:
- Queries analíticas rápidas sobre rangos de tiempo
- Compresión nativa de datos históricos
- Funciones de ventana temporal avanzadas

---

## Grafana y Dashboards

Grafana está preconfigurado mediante provisioning automático:

- **Datasource:** Conexión directa a TimescaleDB (`timescaledb:5432 / energia_db`)
- **Dashboard:** `energia_dashboard.json` cargado automáticamente al iniciar

### Credenciales por defecto

| Campo    | Valor   |
|----------|---------|
| Usuario  | `admin` |
| Password | `admin` |

> Se recomienda cambiar las credenciales en entornos de producción.

---

## Variables de Entorno

### API (`api`)

| Variable  | Default       | Descripción                |
|-----------|---------------|----------------------------|
| `DB_HOST` | `timescaledb` | Host de la base de datos   |
| `DB_PORT` | `5432`        | Puerto PostgreSQL           |
| `DB_NAME` | `energia_db`  | Nombre de la base de datos |
| `DB_USER` | `postgres`    | Usuario de PostgreSQL       |
| `DB_PASS` | `postgres`    | Contraseña de PostgreSQL    |

### Simulador (`data_simulator`)

| Variable   | Default                | Descripción                         |
|------------|------------------------|-------------------------------------|
| `API_URL`  | `http://api:8000/data` | Endpoint de la API                  |
| `INTERVAL` | `5`                    | Segundos entre cada ronda de envíos |

### Grafana (`grafana`)

| Variable                     | Default | Descripción           |
|------------------------------|---------|-----------------------|
| `GF_SECURITY_ADMIN_USER`     | `admin` | Usuario administrador |
| `GF_SECURITY_ADMIN_PASSWORD` | `admin` | Contraseña admin      |

---

## Backups

El directorio `backups/` contiene el archivo `energia_db.sql` con un dump completo de la base de datos.

**Restaurar el backup:**

```bash
# Copiar el backup al contenedor
docker cp backups/energia_db.sql timescaledb:/tmp/energia_db.sql

# Restaurar
docker exec -it timescaledb psql -U postgres -d energia_db -f /tmp/energia_db.sql
```

**Generar un nuevo backup:**

```bash
docker exec timescaledb pg_dump -U postgres energia_db > backups/energia_db_$(date +%Y%m%d).sql
```

---

## Licencia

Este proyecto es de uso educativo y libre distribución.
