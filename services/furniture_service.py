import traceback
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("furniture")  
db_client = client.get_database()  

def object_id(id_str: str) -> ObjectId:
    return ObjectId(id_str)

async def get_all():
    try:
        furnitures = await db_client.furnitures.find().to_list(length=None)

        for furniture in furnitures:
            furniture["_id"] = str(furniture["_id"])
            if "_ownerId" in furniture:
                furniture["_ownerId"] = str(furniture["_ownerId"])

        return furnitures
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching furniture list: {str(e)}")

async def get_one(furniture_id: str):
    try:
        if not ObjectId.is_valid(furniture_id):
            raise HTTPException(status_code=400, detail="Invalid furniture ID.")

        furniture = await db_client.furnitures.find_one({"_id": ObjectId(furniture_id)})

        if not furniture:
            raise HTTPException(status_code=404, detail="Furniture not found.")

        furniture["_id"] = str(furniture["_id"])
        if "_ownerId" in furniture:
            furniture["_ownerId"] = str(furniture["_ownerId"])

        return furniture

    except HTTPException as http_err:
        raise http_err 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching furniture: {str(e)}")


async def update(furniture_id: str, furniture_data: dict):
    await db.furnitures.update_one({"_id": object_id(furniture_id)}, {"$set": furniture_data})
    return await get_one(furniture_id)

async def create(furniture_data: dict):
    try:
        
        new_furniture = await db_client.furnitures.insert_one(furniture_data)
        created_furniture = await db_client.furnitures.find_one({"_id": new_furniture.inserted_id})

        created_furniture["_id"] = str(created_furniture["_id"])
        created_furniture["_ownerId"] = str(created_furniture["_ownerId"])

        return created_furniture

    except Exception as e:
        error_trace = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Furniture creation failed: {str(e)}")

async def delete(furniture_id: str):
    return await db.furnitures.delete_one({"_id": object_id(furniture_id)})