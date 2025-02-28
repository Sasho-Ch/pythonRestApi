from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from services.furniture_service import get_all, get_one, create, update, delete
from motor.motor_asyncio import AsyncIOMotorClient

import os

router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/furniture")
client = AsyncIOMotorClient(MONGO_URI)

db = client["furniture"]  
db_client = client.get_database("furniture")


@router.get("/")
async def get_furnitures():
    try:
        furnitures = await get_all()
        return furnitures
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving furnitures: {str(e)}")

@router.get("/{furniture_id}")
async def get_furniture(furniture_id: str):
    try:
        return await get_one(furniture_id)
    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching furniture: {str(e)}")

@router.put('/{furniture_id}')
async def update_furniture(furniture_id: str, request: Request):
    furniture_data = await request.json()
    return await update(furniture_id, furniture_data)

@router.delete('/{furniture_id}')
async def delete_furniture(furniture_id: str):
    await delete(furniture_id)
    return {"ok": True}


@router.post("/", status_code=201)
async def create_furniture(request: Request):
    if not request.state.user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        furniture_data = await request.json()
        user_id = request.state.user["_id"]

        if not user_id:
            raise HTTPException(status_code=400, detail="User ID missing")

        furniture_data["_ownerId"] = user_id  
        furniture = await create(furniture_data)

        furniture_id = str(furniture["_id"])

        await db_client.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"furnitures": furniture_id}}
        )

        return JSONResponse(content={"message": "Furniture created successfully", "furniture": furniture}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))