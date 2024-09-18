from pydantic import BaseModel, ConfigDict
from datetime import date


class _Base(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class OrganizeModel(_Base):
    user_id: int
    full_name: str
    ogrn: str
    ogrn_date: date
    address: str
    format: str
    region: str
    status: str


class UserResgisetr(_Base):
    login: str
    password: str
    first_name: str
    second_name: str
    last_name: str = None


class UserLogin(_Base):
    login: str
    password: str


class UserInfo(_Base):
    id: int
    login: str
    first_name: str
    second_name: str
    is_organizer: bool
    is_department: bool


class GetUser(_Base):
    id: int
    login: str
    is_organizer: bool
    is_department: bool