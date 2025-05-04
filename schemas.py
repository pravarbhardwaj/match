from pydantic import BaseModel ,Field
from typing import List


class ProfileCreate(BaseModel):
    id: str = Field(..., alias="user_id")
    age: int
    gender: str
    interests: List[str]
    geohash: str



class UserProfileResponse(BaseModel):
    user_id: str
    age: int
    gender: str
    interests: str
    geohash: str

class ActivityOut(BaseModel):
    actor_id: str
    target_id: str
    status: int

