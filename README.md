# Matchmaking API

A FastAPI-based matchmaking backend system that connects users based on proximity, shared interests, and age similarity.

Built with **FastAPI**, **SQLite**, **Redis**, **Geohash**, and **Docker** for performance, simplicity, and scalability.

---

## Features

- User Registration (with age, gender, interests, location)
- Geohash-based location filtering
- Match Scoring (based on interests & age similarity)
- Activity Logging (Match, Block, Dislike)
- Redis Caching for today’s activity
- Dockerized for production-ready deployment

---

## Tech Stack

- FastAPI
- SQLite (with SQLAlchemy ORM)
- Redis
- Python 3.10+
- Docker & Docker Compose
- Alembic for migrations

---


## Installation
- To run using docker first use command ```docker-compose build``` then use 
  ```docker-compose up``` to start the container
- To run it without docker - create virtual environment then run ```pip install -r requirements.txt``` and then run the project using command ```fastapi dev main.py```

---

## Migration

- To run migrations use alembic command ```alembic revision --autogenerate -m "Models Migration"``` and then migrate is using ```alembic upgrade head```

---
### Code Logic
- All the APIs will be listed on localhost:8000/docs url using Swagger
- test script is placed in root with name test_script.py. It can be executed standalone using python with server running or via project api using ```/run_script```
- Test Script has 4 locations with latitudes and longitudes, which uses Faker to create 4 random users with random geohashes in the range of 25 km for the each location and stores it in User table.
- User Activity like match, dislike or block is stored in UserActivity which is used to fetch matches. 
Matches works on the logic where users with action are found from UserActivity table and query is done using the combination of redis and database. All the user activity is stored in database + redis for the day and all activity is fetched using Activity of user for the day from redis and Activity less than today from database. This is done so to avoid lag and slow reads as UserActivity table has composite indexing on actor and targer and status. This is done so to read data faster but since it will have heavy rights as well indexing can not be done on the spot as database will perform slower. So to avoid for today's activity data is read from Redis and indexed data (which will be done in off times) will be read from Database (Something which twitter does!)
- To action on some profile using a profile ```/take_action``` api can be and actor and target id can be procured from ```/match/{user_id}``` API.
---

### Scoring Logic
- Scoring logic in Match is written so to have +10 on each interest matched.

- Scoring using age:\
    Calculate Age Difference:\
    The absolute difference between the ages of the two users  is computed using abs(user1-user2). This ensures the result is always positive, regardless of which age is larger.

    Divide by 2:\
    The age difference is divided by 2 using integer division (// 2). This reduces the impact of the age difference on the score.

    Subtract from 10:
    The result from step 2 is subtracted from 10. This means smaller age differences result in higher scores, while larger age differences reduce the score.

    Clamp to a Minimum of 0:
    The function ensures that the score does not go below 0. If the calculated value is negative, it is set to 0.


###  Local Setup

```bash
git clone https://github.com/pravarbhardwaj/match.git
cd match
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
