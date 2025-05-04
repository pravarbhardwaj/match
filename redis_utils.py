import redis
import json
from datetime import datetime

# Redis client setup
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Utility to get today's date
def get_today_date():
    return datetime.today().date()

def get_seconds_until_eod():
    now = datetime.now()
    eod = datetime.combine(now.date(), datetime.max.time())
    return int((eod - now).total_seconds())

# Store today's activities in Redis with TTL of 24 hours (86400 seconds)
def store_today_activity_in_redis(user_id, activity_data):
    today = get_today_date()
    redis_key = f"activity:{today}:{user_id}"
    r.rpush(redis_key, json.dumps(activity_data))  # Append to list
    r.expire(redis_key, get_seconds_until_eod())


# Get today's activities from Redis
def get_today_activities_from_redis(user_id):
    today = get_today_date()
    redis_key = f"activity:{today}:{user_id}"
    activity_list = r.lrange(redis_key, 0, -1)
    return [json.loads(item.decode("utf-8")) for item in activity_list]

