from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
import os 

JWT_SECRET = os.getenv("JWT_SECRET")

async def auth_middleware(request: Request, call_next):
    token = request.cookies.get("auth_token")

    if not token: 
        request.state.user = None
        return await call_next(request)
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        request.state.user = payload
    except JWTError:
        response = JSONResponse(content={"message": "Invalid token."}, status_code=401)
        response.delete_cookie("auth_token")
        request.state.user = None
        return response
    
    response = await call_next(request)
    return response

def is_auth(request: Request):
    if not request.state.user:
        raise HTTPException(status_code=401, detail="Unauthorized access.")
    
def is_guest(request: Request):
    if request.state.user:
        raise HTTPException(status_code=403, detail="Already logged in.")