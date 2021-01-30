import datetime as dt
from typing import List, Any

from pydantic import BaseModel


class Property(BaseModel):
    name: str
    value: Any


class Entity(BaseModel):
    id: str = None
    entity_name: str
    entity_type: str = None
    properties: List[Property] = None
    create_time: dt.datetime = None


class Relation(BaseModel):
    id: str = None
    start_entity_id: str
    start_entity_kg_id: str = None
    end_entity_id: str
    end_entity_kg_id: str = None
    relation_type: str
    create_time: dt.datetime = None


class SCHEMA_TYPE:
    ENTITY = 'entity_type'
    RELATION = 'relation_type'
    PROPERTY = 'property_type'


class SchemaType(BaseModel):
    id: str = None
    name: str
    schema_type: str
    create_time: dt.datetime = None
