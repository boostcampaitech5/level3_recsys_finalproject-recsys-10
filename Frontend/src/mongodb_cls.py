import yaml
import ast
import urllib.parse
import numpy as np
from pymongo import MongoClient

class MongoDB_cls:
    def __init__(self):
        """
        Initializes a MongoDB client with the provided connection configuration.
        Args:
            None
        Returns:
            None
        """
        with open('_key/mongodb_key.yaml') as config_file:
            config = yaml.safe_load(config_file)
        connect_id = urllib.parse.quote_plus(config['id'])
        connect_password = urllib.parse.quote_plus(config['password'])
        connect_ip, connect_port = config['ip'], config['port']
        self.client = MongoClient(f'mongodb://{connect_id}:{str(connect_password)}@{connect_ip}:{connect_port}')
        

    def get_database(self, database_name: str):
        """
        Retrieves a MongoDB database instance based on the provided database name.
        Args:
            database_name (str): The name of the MongoDB database.
        Returns:
            pymongo.database.Database: The MongoDB database instance.
        """
        return self.client[database_name]
    

    def get_collection(self, database_name: str, collection_name: str):
        """
        Retrieves a MongoDB collection instance based on the provided database and collection names.
        Args:
            database_name (str): The name of the MongoDB database.
            collection_name (str): The name of the MongoDB collection.
        Returns:
            pymongo.collection.Collection: The MongoDB collection instance.
        """
        database = self.get_database(database_name)
        return database[collection_name]
    

    def login(self, username: str, password: str) -> bool:
        """
        Authenticates a user by checking the provided username and password against the stored user credentials.
        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        Returns:
            bool: True if the authentication is successful, False otherwise.
        """
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        user = collection.find_one({"username": username})
        if user and user["password"] == password:
            return True
        return False


    def load_thumbnail(self, recipeid:int) -> str:
        """
        Retrieves the thumbnail link associated with the given recipe ID.
        Args:
            recipeid (int): The ID of the recipe.
        Returns:
            str: The URL of the thumbnail image.
        """
        collection = self.get_collection('recipe_app_db', 'thumbnail_data')
        reciped_data = collection.find_one({"recipeid": recipeid})
        recipeid_thumbnail = reciped_data['thumb_link']
        return recipeid_thumbnail
    

    def load_title(self, recipeid:int) -> str:
        """
        Retrieves the title associated with the given recipe ID.
        Args:
            recipeid (int): The ID of the recipe.
        Returns:
            str: The title of the recipe.
        """
        collection = self.get_collection('recipe_app_db', 'ingresync_recipe_data')
        reciped_data = collection.find_one({"recipeid": recipeid})
        recipeid_title = reciped_data['title']
        return recipeid_title
    
    def load_recipe_info(self, recipeid:int) -> tuple:
        """
        Retrieves the recipe information associated with the given recipe ID.
        Args:
            recipeid (int): The ID of the recipe.
        Returns:
            tuple: A tuple containing ingredients, ingredient_quantity, and process.
        """
        collection = self.get_collection('recipe_app_db', 'ingresync_recipe_data')
        reciped_data = collection.find_one({"recipeid": recipeid})
        ingredients = reciped_data['ingredients']
        ingredient_quantity = reciped_data['ingredient_quantity']
        process = reciped_data['process']
        return ingredients, ingredient_quantity, process
    
    def load_user_favorite_food_list(self, username: str) -> list:
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        user = collection.find_one({"username": username})
        favorite_food_list = user['favorite_food']
        favorite_food_list = ast.literal_eval(favorite_food_list)
        return favorite_food_list
    
    def update_user_favorite_food_list(self, username: str, favorite_food_list: list):
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        user_data = collection.find_one({"username": username})
        user_data["favorite_food"] = str(favorite_food_list)
        filter = {"username": username}
        collection.replace_one(filter, user_data)

    def load_category_idx_to_recipeid(self, cate_list: list) -> list:
        collection = self.get_collection('recipe_app_db', 'category_idx_data')
        cursor = collection.find({
            #"cat1": cate_list[0],
            "cat2": cate_list[1],
            "cat3": cate_list[2],
            "cat4": cate_list[3],
        })
        try:
            output = [document['recipeid'] for document in cursor]
        except:
            output = []
        return output
    
    # ------------------------------------------------------------------------------- #

    def load_all_user_list(self) -> str:
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        cursor = collection.find({})
        try:
            output = [document['username'] for document in cursor]
        except:
            output = []
        return output
    
    def load_user_category_onehot_list(self, username: str) -> list:
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        user = collection.find_one({"username": username})
        favorite_food_list = user['favorite_category']
        favorite_food_list = ast.literal_eval(favorite_food_list)
        return favorite_food_list

    def load_category_onehot_list(self, recipeid:int) -> list:
        collection = self.get_collection('recipe_app_db', 'category_onehot_data')
        onehot_list = collection.find_one({"recipeid": recipeid})
        onehot_list = onehot_list['category_list']
        onehot_list = ast.literal_eval(onehot_list)
        return onehot_list

    def add_category_onehot(self, username: str, recipeid:int):
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        user_data = collection.find_one({"username": username})
        origin_onehot_np = np.array(ast.literal_eval(user_data["favorite_category"]))
        onehot_np = np.array(self.load_category_onehot_list(recipeid))
        result = origin_onehot_np + onehot_np
        user_data["favorite_category"] = str(list(result))
        filter = {"username": username}
        collection.replace_one(filter, user_data)


    def sub_category_onehot(self, username: str, recipeid:int):
        collection = self.get_collection('recipe_app_db', 'user_login_db')
        user_data = collection.find_one({"username": username})
        origin_onehot_np = np.array(ast.literal_eval(user_data["favorite_category"]))
        onehot_np = np.array(self.load_category_onehot_list(recipeid))
        result = origin_onehot_np - onehot_np
        user_data["favorite_category"] = str(list(result))
        filter = {"username": username}
        collection.replace_one(filter, user_data)