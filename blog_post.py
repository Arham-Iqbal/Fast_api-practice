from fastapi import FastAPI,HTTPException,Depends ,Header
from pydantic import BaseModel
from passlib.context import CryptContext
from pymongo import MongoClient
import jwt
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError
from uuid import UUID, uuid4
from bson import ObjectId

app=FastAPI()
SECRET_KEY = "arhamsecret123"
ALGORITHM = "HS256"

client = MongoClient("mongodb://localhost:27017")
db = client["mydatabase"]

users_collection = db["users"]
blogs_collection = db["blogs"]

id=uuid4()


class blog_content(BaseModel):
    title:str
    content:str
    

class Author(BaseModel):
    username:str
    password:str



pwd_context=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"

)



def hashpass(password:str):
    return pwd_context.hash(password)


def verify_password(plain_pass,hash_pass):
    return pwd_context.verify(plain_pass,hash_pass)


def create_token(data:dict):
    token=jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)
    return token
def verify_token(token:str):
    try:
       payload=jwt.decode(token,SECRET_KEY,algorithm=ALGORITHM)
       return payload
    except:
        raise HTTPException(status_code=401,detail="invalid token")
# get current user from header
def get_current_user(authorization: str = Header()):
    
    token = authorization.split(" ")[1]

    payload = verify_token(token)

    return payload["authorid"]

@app.post("/register")
def register(author:Author):
    existing_user=users_collection.find_one({"username":author.username})
    if existing_user:
        raise HTTPException(status_code=400,detail="user already exist")
    hashed=hashpass(author.password)
    users_collection.insert_one({
        "username":author.username,
        "password":hashed

    })
    return{"message":"author registered successfully"}

@app.post("/login")
def login(author:Author):
    author_user=users_collection.find_one({"username":author.username})
    if not author_user:
        raise HTTPException(status_code=401,detail="author username not available")
    if not verify_password(author.password,author_user["password"]):
        raise HTTPException(status_code=400,detail="password is not correct")
    
    token=create_token({
        "authorid":str(author_user["_id"])
    })
    
    return{"message":"login successfull","token":token}



@app.post("/postblog")
def postblog( post: blog_content,
    current_user=Depends(get_current_user)):

    blogs_collection.insert_one({
        "title":post.title,
        "content":post.content,
        "author_id": ObjectId(current_user)

    })
    return{"message":"Blog posted successfully"}