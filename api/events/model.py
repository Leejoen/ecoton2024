from __future__ import annotations

from typing import List, Any

from pydantic import BaseModel, ConfigDict, model_validator, Field
from datetime import datetime, date


class _Base(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class MetroLine(_Base):
    id: int
    name: str
    color: str


class MetroStationModel(_Base):
    id: int
    name: str
    line_info: MetroLine


class CreateEvent(_Base):
    name: str
    short_description: str
    description: str
    date_start: datetime
    place: str
    metro_station_id: int


class Event(_Base):
    id: int
    name: str
    short_description: str  
    date_start: datetime
    place: str
    metro_info: MetroStationModel


class GetEvents(_Base):
    events: list[Event]