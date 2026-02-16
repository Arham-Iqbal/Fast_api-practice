from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import jwt
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pymongo import MongoClient
app=FastAPI()
SECRET_KEY = "arhamsecret123"
ALGORITHM = "HS256"

client = MongoClient("mongodb://localhost:27017")
db = client["mydatabase"]

users_collection = db["users"]
class User(BaseModel):
    name:str
    password:str



pwd_context=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"

)

def create_token(data:dict):
    token=jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)
    return token
def verify_token(token:str):
    try:
       payload=jwt.decode(token,SECRET_KEY,algorithm=ALGORITHM)
       return payload
    except:
        raise HTTPException(status_code=401,detail="invalid token")


def hash_pass(password:str):
    return pwd_context.hash(password)


def verifypass(plain_pass,hashed_pass):
    return pwd_context.verify(plain_pass,hashed_pass)


@app.post("/register")
def create_user(user:User):
   existing_user=users_collection.find_one({"name":user.name})
   if existing_user:
       raise HTTPException(status_code=400,detail="user already exist")
   hashed=hash_pass(user.password)
   
   users_collection.insert_one({
       "name":user.name,
       "password":hashed
   })
   return{"message":"new user created succefffully"}




@app.post("/login")
def login(user:User):
    db_user=users_collection.find_one({"name":user.name})
    if not db_user:
        raise HTTPException(status_code=400,detail="user not found")
    if not verifypass(user.password,db_user["password"]):
        raise HTTPException(status_code=400,detail="password incorrect")
    token=create_token({
        "name":user.name
    })
    return{"message":"login successfull","token":token}


@app.get("/protected")
def testtoken(token:str):
    payload=verify_token(token)
    return {
        "message": "Access granted",
        "user": payload
    }

@app.get("/me")
def get_me(token: str):

    payload = verify_token(token)

    return payload
