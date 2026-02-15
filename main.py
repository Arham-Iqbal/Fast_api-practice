from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
users_collection = client["userdb"]["users"]
try:
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("DB connected")
except Exception:
    print("DB not connected")

class User(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(user: User):
    user_dict = user.dict()
    user_dict["_id"] = str(users_collection.insert_one(user_dict).inserted_id)
    return user_dict

@app.get("/users")
def get_users():
    return [{**u, "_id": str(u["_id"])} for u in users_collection.find()]

@app.get("/users/{id}")
def get_user(id: str):
    try:
        user = users_collection.find_one({"_id": ObjectId(id)})
        if user:
            user["_id"] = str(user["_id"])
            return user
        return {"error": "user not found"}
    except Exception:
        return {"error": "invalid user id format"}

@app.get("/")
def default():
    return {"message": "welcome buddy"}

