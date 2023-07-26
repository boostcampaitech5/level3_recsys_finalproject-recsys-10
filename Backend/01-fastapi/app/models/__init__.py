from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.config import MONGO_DB_NAME, MONGO_DB_URL

from app.models.models import Category, IngreSync, Sequence, Thumbnail, User_Login, Response

class MongoDB:
    def __init__(self):
        self.client = None
        self.engine = None

    def connect(self):
        self.client = MongoClient(MONGO_DB_URL)
        self.engine = self.client.get_database(MONGO_DB_NAME)
        print("DB와 연결되었습니다.")
    
    def close(self):
        self.client.close()


mongodb = MongoDB()

__all__ = ["Category", "IngreSync", "Sequence", "Thumbnail", "User_Login", "Response"]