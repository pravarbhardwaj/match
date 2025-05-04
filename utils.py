import geohash
import math
from sqlalchemy.orm import Session
from models import User

def get_nearby_geohashes(user_geohash: str):
    neighbors = geohash.neighbors(user_geohash)
    neighbors.append(user_geohash)
    return neighbors

