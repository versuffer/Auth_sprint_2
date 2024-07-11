from pydantic import BaseModel


class HashedRegistrationData(BaseModel):
    hashed_password: str
    dynamic_salt: str
