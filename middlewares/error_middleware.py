from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

async def exception_handler(request, exc):
    status_code = getattr(exc, "status_code", 500)
    message = str(exc)

    return JSONResponse(status_code=status_code, content={"message": message})