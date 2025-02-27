from pydantic import BaseModel, Field
from bson import ObjectId

class FurnitureBase(BaseModel):
    model: str
    year: str
    description: str
    price: str
    img: str
    material: str | None

class FurnitureDB(FurnitureBase):
    id: ObjectId = Field(alias="_id", default=None)
    _ownerId: ObjectId

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId : str}
    