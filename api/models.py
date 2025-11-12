from pydantic import BaseModel
from datetime import datetime

class Measurement(BaseModel):
    sensor_id: int
    timestamp: datetime
    value: float
    type: str
    location: str
