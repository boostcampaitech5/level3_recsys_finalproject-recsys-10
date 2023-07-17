import yaml
import urllib.parse
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