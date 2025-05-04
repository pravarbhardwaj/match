from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response, JSONResponse
from deps import get_db
from models import *
from schemas import *
from database import SessionLocal
import redis
from typing import List
from sqlalchemy.orm import Session
from redis_utils import store_today_activity_in_redis, get_today_activities_from_redis
import traceback
from utils import get_nearby_geohashes
from test_script import run_test

app = FastAPI()

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/profiles/{user_id}", response_model=UserProfileResponse)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()

    if user is None:
        return Response(status_code=404, detail="User not found")
    
    profile = UserProfileResponse(
        user_id=user.user_id,
        age=user.age,
        gender=user.gender,
        interests=user.interests,
        geohash=user.geohash
    )
    
    return profile


@app.get("/profiles", response_model=List[UserProfileResponse])
def get_all_profiles(db: Session = Depends(get_db)):
    """
    API to get all user profiles.
    """
    try:
        users = db.query(User).all()
        if not users:
            return JSONResponse({"message": "No users found"}, status_code=404)
        return users
    except Exception as e:
        print("Error fetching profiles:", e)
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/profiles")
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.user_id == profile.id).first()
    if existing:
        return JSONResponse({"message": "User already exists"}, status_code=400)
    try:
        user = User(
            user_id=profile.id,
            age=profile.age,
            gender=profile.gender,
            interests=','.join(profile.interests),
            geohash=profile.geohash
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"status": "created", "user": user.user_id}
    except Exception as e:
        print("Error creating profile:", e)
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/match/{user_id}")
def match_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return JSONResponse({"message": "User found"}, status_code=404)

        geohash_neighbors = get_nearby_geohashes(user.geohash)

        
        candidates = db.query(User).filter(User.geohash.in_(geohash_neighbors), User.user_id != user_id).all()

        today_activities = get_today_activities_from_redis(user_id)
        today_excluded = {a["target_id"] for a in today_activities}

        today_date = datetime.datetime.today()
        past_activities = db.query(UserActivity).filter(
            UserActivity.actor_id == user_id,
            UserActivity.timestamp < today_date
        ).all()
        past_excluded = {a.target_id for a in past_activities}

        excluded_ids = today_excluded.union(past_excluded)

        matches = []
        user_interests = set(user.interests.split(","))

        for c in candidates:
            if c.user_id in excluded_ids:
                continue

            candidate_interests = set(c.interests.split(","))
            shared = user_interests & candidate_interests

            shared_score = len(shared) * 10
            age_penalty = abs(user.age - c.age)    
            age_score = max(0, 10 - (age_penalty // 2))  

            total_score = shared_score + age_score

            matches.append((total_score, c))

        matches.sort(reverse=True, key=lambda x: x[0])

        top_matches = [
            {
                "user_id": m.user_id,
                "age": m.age,
                "gender": m.gender,
                "interests": m.interests.split(","),
                "score": score
            }
            for score, m in matches[:5] if score > 0
        ]
        return {"matches": top_matches}
    except Exception as e:
        print("Error matching user:", e)
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/activity/{user_id}")
def store_activity(user_id: str, activity_data: dict, db: Session = Depends(get_db)):
    try:
        today = datetime.datetime.today().date()

        activity = UserActivity(
            actor_id=activity_data["actor_id"],
            target_id=activity_data["target_id"],
            status=activity_data["status"],
            timestamp=today
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        store_today_activity_in_redis(user_id, activity_data)
        
        return {"status": "success", "activity_id": activity.id}
    except Exception as e:
        print("Error storing activity:", e)
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get("/activity/{user_id}", response_model=List[ActivityOut])
def get_user_activity(user_id: str, db: Session = Depends(get_db)):
    activities = db.query(UserActivity).filter(UserActivity.actor_id == user_id).all()
    if not activities:
        raise HTTPException(status_code=404, detail="No activity found for user")
    return activities

@app.post("/action")
def take_action(
    actor_id: str,
    target_id: str,
    decision: int, 
    db: Session = Depends(get_db)
):
    try:
        if actor_id == target_id:
            raise HTTPException(status_code=400, detail="Actor and target cannot be the same.")

        today = datetime.date.today()

        # Save to DB
        activity = UserActivity(
            actor_id=actor_id,
            target_id=target_id,
            status=decision,
            timestamp=today
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        # Save to Redis
        activity_data = {
            "actor_id": actor_id,
            "target_id": target_id,
            "status": decision,
            "timestamp": str(today)
        }
        store_today_activity_in_redis(actor_id, activity_data)

        return {"status": "success", "message": "Action recorded", "activity_id": activity.id}

    except Exception as e:
        print("Error in take_action:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/run_script')
def run_script():
    """
    Endpoint to trigger the script.
    """
    try:
        # Call your script function here
        # For example: my_script_function()
        run_test()
        return {"message": "Script executed successfully"}
    except Exception as e:
        print("Error running script:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")