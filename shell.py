from database import SessionLocal
from models import *
from sqlalchemy.orm import Session

db: Session = SessionLocal()

print("Interactive shell loaded.")
print("Use `db` for queries. Example: db.query(User).all()")