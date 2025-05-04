import requests
import geohash 
import random
from faker import Faker
import math

fake = Faker()
BASE_URL = "http://127.0.0.1:8000"
GEOHASH_PRECISION = 5


LOCATIONS = [
    (13.7563, 100.5018),    # Bangkok
    (37.7749, -122.4194),   # San Francisco
    (48.8566, 2.3522),      # Paris
    (35.6895, 139.6917),    # Tokyo
]

ALL_USERS = []

def random_offset_within_radius(lat, lon, radius_km=25):
    """
    Returns a random point within the given radius (km) around the input latitude and longitude.
    """
    radius_deg = radius_km / 111  # Rough conversion from km to degrees

    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, radius_deg)

    delta_lat = distance * math.cos(angle)
    delta_lon = distance * math.sin(angle) / math.cos(math.radians(lat))

    return lat + delta_lat, lon + delta_lon

def create_profile(user):
    response = requests.post(f"{BASE_URL}/profiles", json=user)
    if response.status_code == 200:
        print(f"Created user {user['user_id']} in quadrant {user['geohash']}")
    else:
        print(f"Failed to create user: {response.text}")

def check_user_profile(user_id):
    """
    Function to check if the user profile exists by calling the GET /profiles/{user_id} endpoint.
    Returns True if the user exists, False otherwise.
    """
    response = requests.get(f"{BASE_URL}/profiles/{user_id}")
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        print(f"User {user_id} not found.")
        return False
    else:
        print(f"Error checking user {user_id}: {response.status_code} - {response.text}")
        return False

def create_activity(actor_id, target_id, status):
    actor_exists = check_user_profile(actor_id)
    target_exists = check_user_profile(target_id)
    if not actor_exists or not target_exists:
        print(f"Cannot create activity. Actor or target profile does not exist.")
        return

    activity = {
        "actor_id": actor_id,
        "target_id": target_id,
        "status": status  
    }
    res = requests.post(f"{BASE_URL}/activity/{actor_id}", json=activity)
    if res.status_code == 200:
        print(f"Activity: {actor_id} -> {target_id} (status: {status})")
    else:
        print(f"Failed activity post: {res.text}")


def run_test():
    print("Creating users in each quadrant...\n")
    for lat, lon in LOCATIONS:
        ghash = geohash.encode(lat, lon, precision=GEOHASH_PRECISION)
        for _ in range(4):
            rand_lat, rand_lon = random_offset_within_radius(lat, lon, radius_km=25)
            ghash = geohash.encode(rand_lat, rand_lon, precision=GEOHASH_PRECISION)
            user_id = fake.uuid4()
            user = {
                "user_id": user_id,  
                "age": random.randint(20, 40),
                "gender": random.choice(["M", "F"]),
                "interests": random.sample(["music", "tech", "sports", "travel", "art", "food"], 3),
                "geohash": ghash
            }
            create_profile(user)
            ALL_USERS.append(user)
    
    if not ALL_USERS:
        print("No users created. Exiting.")
        return
    

if __name__ == "__main__":
    run_test()
