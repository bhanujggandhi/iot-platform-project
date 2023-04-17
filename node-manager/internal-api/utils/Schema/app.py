from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class SensorType(str, Enum):
    AQ = "AQ"
    WMWD = "WM-WD"
    WMWF = "WM-WF"
    WE = "WE"
    SROC = "SR-OC"
    SREM = "SR-EM"
    SRAQ = "SR-AQ"
    SRAC = "SR-A"
    CM = "CM"
    SL = "SL"
    EM = "EM"
    WN = "WN"


class AppRegister(BaseModel):
    name: str
    sensor_types: List[SensorType]
    binded_sensors: List[str]

    class Config:
        orm_mode = True
