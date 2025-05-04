import geohash
import math
from sqlalchemy.orm import Session
from models import User

# Function to get the neighboring geohashes of the target user's geohash
def get_nearby_geohashes(user_geohash: str):
    # Get the neighboring geohashes
    neighbors = geohash.neighbors(user_geohash)
    # Add the user's own geohash to the neighbors list
    neighbors.append(user_geohash)
    return neighbors

