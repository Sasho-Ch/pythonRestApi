from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

from routes.routes import router as api_router
from middlewares.auth_middleware import auth_middleware
from middlewares.error_middleware import exception_handler

load_dotenv()   

app = FastAPI()

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(auth_middleware)

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database()

JWT_SECRET = os.getenv("JWT_SECRET")

app.include_router(api_router)
app.add_exception_handler(Exception, exception_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)