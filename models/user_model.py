from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class UserBase(BaseModel):
    username: str
    email: EmailStr
    tel: str

class UserCreate(UserBase):
    password: str
    repassword: str = None  

class UserDB(UserBase):
    id: ObjectId = Field(alias="_id", default=None)
    password: str
    furnitures: list[ObjectId] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    def set_password(self, password: str):
        self.password = hash_password(password)

    def check_password(self, password: str) -> bool: 
        return verify_password(password, self.password)
