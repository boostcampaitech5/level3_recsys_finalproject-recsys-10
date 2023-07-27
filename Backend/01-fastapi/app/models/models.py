import uuid
from typing import Optional, List, Any
from pydantic import BaseModel, Field


from datetime import datetime

class Category(BaseModel):
    _id: str = Field(default_factory=uuid.uuid4)
    reciptid : int
    cat1 : int
    cat2 : int
    cat3 : int
    thumb_link : str

class IngreSync(BaseModel):
    _id : str =Field(default_factory=uuid.uuid4)
    recipeid : int
    title : str
    cook : str
    quantity : str
    time: str
    level : str
    ingredients : List[str] = Field(default_factory=list)
    ingredient_quantity : List[str]  = Field(default_factory=list)
    process : List[str] = Field(default_factory=list)
    view :  int

class Sequence(BaseModel):
    _id : str =Field(default_factory=uuid.uuid4)
    uid : int
    rid : int
    time: datetime = Field(default_factory=datetime.now)
    star : int

class Thumbnail(BaseModel):
    _id : str =Field(default_factory=uuid.uuid4)
    recipeid :  int
    thumbnail_link : str

class User_Login(BaseModel):
    _id : str =Field(default_factory=uuid.uuid4)
    username : str
    password : str
    favorite_category : List[int]
    favorite_food : List[int]
    user_id : int


class Response(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any]

    class Config:
        schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation successful",
                "data": "Sample data",
            }
        }
    