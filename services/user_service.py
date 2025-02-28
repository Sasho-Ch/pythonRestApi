from bson import ObjectId
from fastapi import HTTPException
from models.user_model import hash_password
from motor.motor_asyncio import AsyncIOMotorClient
from jose import jwt
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET")
db_client = AsyncIOMotorClient(os.getenv("MONGO_URI")).get_database()

async def register(user_data: dict):
    if "rePassword" in user_data:
        del user_data["rePassword"]
    
    existing_user = await db_client.users.find_one({"email": user_data["email"]})
    if existing_user:
        raise ValueError("Email is already registered.")

    user_data["password"] = hash_password(user_data["password"])
    user_data["furnitures"] = [] 

    new_user = await db_client.users.insert_one(user_data)
    created_user = await db_client.users.find_one({"_id": new_user.inserted_id}, {"repassword": 0})
    return generate_access_token(created_user)

async def login(user_data: dict):
    try:
        user = await db_client.users.find_one({"email": user_data["email"]})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        stored_password = user["password"]
        if not pwd_context.verify(user_data["password"], stored_password):
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        access_token_data = generate_access_token(user)  
        access_token = access_token_data["accessToken"]  

        user["_id"] = str(user["_id"])
        user["furnitures"] = [str(f_id) for f_id in user.get("furnitures", [])]

        
        return {
            "_id": user["_id"],
            "username": user["username"],
            "email": user["email"],
            "tel": user["tel"],
            "furnitures": user["furnitures"],
            "accessToken": access_token 
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

async def get_profile(user_id: str):
    try:
        user = await db_client.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        user["_id"] = str(user["_id"])
        user["furnitures"] = [str(f_id) for f_id in user.get("furnitures", [])]

        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user profile: {str(e)}")
    
async def get_one(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format.")

        user = await db_client.users.find_one(
            {"_id": ObjectId(user_id)}, 
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        user["_id"] = str(user["_id"])
        user["furnitures"] = [str(f_id) for f_id in user.get("furnitures", [])]

        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

async def edit_profile(user_id: str, updated_data: dict):
    try:
        user = await db_client.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        if "password" in updated_data and updated_data["password"]:
            updated_data["password"] = hash_password(updated_data["password"])

        updated_data.pop("repassword", None)

        await db_client.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})

        updated_user = await db_client.users.find_one(
            {"_id": ObjectId(user_id)},
        )

        updated_user["_id"] = str(updated_user["_id"])
        updated_user["furnitures"] = [str(f_id) for f_id in updated_user.get("furnitures", [])]

        return updated_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user profile: {str(e)}")

def generate_access_token(user: dict):
    access_token = jwt.encode({"_id": str(user["_id"]), "email": user["email"]}, JWT_SECRET, algorithm="HS256")
    return {"_id": str(user["_id"]), "email": user["email"], "username": user["username"], "tel": user["tel"], "accessToken": access_token}