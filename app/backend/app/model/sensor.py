from typing import Optional
from enum import Enum, IntEnum
from pydantic import BaseModel


class SensorStatusEnum(str, Enum):
    up = "up"
    down = "down"


class SensorLiquidEnum(IntEnum):
    empty = 0
    not_empty = 2


class SensorState(BaseModel):
    status: Optional[SensorStatusEnum] = SensorStatusEnum.down
    liquid: Optional[SensorLiquidEnum] = SensorLiquidEnum.empty


class SensorLocation(BaseModel):
    floor: int = 0
    coords: tuple[int, int] = (0, 0)


class Sensor(BaseModel):
    id: str
    desc: str
    plan: SensorLocation
    state: Optional[SensorState]
