import uvicorn

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, create_engine, Session, Field
from typing import Dict


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    cpf: str
    number: str
    
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    cpf: str
    number: str


DATABASE_URL = "sqlite:///./users.sqlite3"

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

app = FastAPI()

@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    db = Session(engine)
    db.begin()
    user_db = User.from_orm(user)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    db.close()
    return user_db

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    db = Session(engine)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.close()
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate):
    db = Session(engine)
    existing_user = db.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(existing_user, key, value)
    db.add(existing_user)
    db.commit()
    db.refresh(existing_user)
    db.close()
    return existing_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = Session(engine)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    db.close()
    return {"message": "User deleted successfully"}

@app.get("/users/", response_model=list[User])
def get_all_users():
    db = Session(engine)
    users = db.exec(db.query(User)).all()
    db.close()
    return list(user[0].dict() for user in users)


if __name__ == "__main__":
    uvicorn.run(app, port=8000,host='0.0.0.0')
    
