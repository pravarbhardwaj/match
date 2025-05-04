from sqlalchemy import Column, Integer, String, DateTime, func, Float, ForeignKey
from database import Base
from sqlalchemy import Index
from enum import IntEnum
import datetime
import pytz

class ActivityStatus(IntEnum):
    BLOCKED = 1
    DISLIKED = 2
    MATCHED = 3

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    interests = Column(String)
    geohash = Column(String, index=True)  # Add geohash with index for optimized querying


class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True)
    actor_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    target_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    
    status = Column(Integer, index=True) 
    timestamp = Column(DateTime, default=datetime.datetime.now().astimezone(pytz.timezone("UTC")), index=True)

    __table_args__ = (
        Index("ix_actor_target_status", "actor_id", "target_id", "status"),
    )
