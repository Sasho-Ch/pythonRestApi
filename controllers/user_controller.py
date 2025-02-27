import traceback
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Request
from services.user_service import register, login, get_profile, get_one, edit_profile
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/register")
async def register_user(request: Request):
    user_data = await request.json()
    
    user_data.pop("repassword", None)

    try:
        result = await register(user_data)
        response = JSONResponse(content=result)
        response.set_cookie(
            key="auth_token",
            value=result["accessToken"],
            httponly=True,
            samesite="Lax",
            secure=False,
            max_age=3 * 60 * 60
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/login")
async def login_user(request: Request):
    try:
        user_data = await request.json()
        result = await login(user_data)

        response = JSONResponse(content=result)
        response.set_cookie(
            key="auth_token",
            value=result["accessToken"],
            httponly=True,
            samesite="Lax",
            secure=False  
        )

        return response
    except HTTPException as http_err:
        raise http_err  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")
    
@router.post('/logout')
async def logout_user():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="auth_token")
    return response

@router.get("/profile")
async def user_profile(request: Request):
    try:
        if not request.state.user:
            raise HTTPException(status_code=401, detail="Unauthorized: No user session found.")

        user_id = request.state.user["_id"]

        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format.")

        user_profile = await get_profile(user_id)

        return user_profile
    except HTTPException as http_err:
        raise http_err  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching profile: {str(e)}")

@router.get("/{userId}")
async def get_user(userId: str):
    try:
        user = await get_one(userId)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

@router.put("/profile")
async def update_profile(request: Request):
    try:
        if not request.state.user:
            raise HTTPException(status_code=401, detail="Unauthorized: No user session found.")

        user_id = request.state.user["_id"]

        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format.")

        updated_data = await request.json()

        updated_profile = await edit_profile(user_id, updated_data)

        return updated_profile
    except HTTPException as http_err:
        raise http_err  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")