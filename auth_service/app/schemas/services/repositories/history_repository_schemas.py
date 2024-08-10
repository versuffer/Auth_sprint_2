import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class HistoryDBSchema(BaseModel):
    id: uuid.UUID
    auth_date: datetime.datetime
    user_agent: str

    model_config = ConfigDict(from_attributes=True)


class UserHistoryDBSchema(BaseModel):
    user_id: uuid.UUID = Field(alias='id')
    user_history: list[HistoryDBSchema] = Field(alias='history')

    model_config = ConfigDict(from_attributes=True)
