from dao.base import BaseDAO
from database.schemas import EcoEvent


class EcoEventDAO(BaseDAO):
    schema = EcoEvent