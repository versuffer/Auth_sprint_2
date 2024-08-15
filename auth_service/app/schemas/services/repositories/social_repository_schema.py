import uuid

from pydantic import BaseModel, ConfigDict


class SocialDBSchema(BaseModel):

    user_id: uuid.UUID
    social_id: str
    social_name: str

    model_config = ConfigDict(from_attributes=True)


# class SocialCreateDBSchema(BaseModel):
#
#     user_id: uuid.UUID
#     social_id: str
#     social_name: str
#
#     model_config = ConfigDict(from_attributes=True)
