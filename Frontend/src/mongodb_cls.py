import yaml
import urllib.parse
from pymongo import MongoClient

class MongoDB_cls:
    def __init__(self):
        with open('_key/mongodb_key.yaml') as config_file:
            config = yaml.safe_load(config_file)
        connect_id = urllib.parse.quote_plus(config['id'])
        connect_password = urllib.parse.quote_plus(config['password'])
        connect_ip, connect_port = config['ip'], config['port']
        self.client = MongoClient(f'mongodb://{connect_id}:{str(connect_password)}@{connect_ip}:{connect_port}')
        
    def get_database(self, database_name: str):
        return self.client[database_name]
    
    def get_collection(self, database_name: str, collection_name: str):
        database = self.get_database(database_name)
        return database[collection_name]
    
    def login(self, username: str, password: str) -> bool:
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        user = collection.find_one({"username": username})
        if user and user["password"] == password:
            return True
        return False

    def load_thumbnail(self, recipeid:int) -> str:
        collection = self.get_collection('recipe_app_db', 'thumbnail_data')
        reciped_data = collection.find_one({"recipeid": recipeid})
        recipeid_thumbnail = reciped_data['thumb_link']
        return recipeid_thumbnail
    
    def load_title(self, recipeid:int) -> str:
        collection = self.get_collection('recipe_app_db', 'ingresync_recipe_data')
        reciped_data = collection.find_one({"recipeid": recipeid})
        recipeid_title = reciped_data['title']
        return recipeid_title