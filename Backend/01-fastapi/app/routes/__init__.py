from fastapi import APIRouter, Body, Request
from typing import List
from fastapi.encoders import jsonable_encoder
from app.models import *
from app.models import mongodb

router = APIRouter()

@router.get("/", response_model=Response)
async def get_path():
    return {
            "status_code": 200,
            "response_type": "success",
            "description": "Recipes data retrieved successfully",
            "data": path
        }

@router.get("/list", response_model=Response)
async def root(request: Request):
    recipes = await retrieve_recipe_list()
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Recipes data retrieved successfully",
        "data": recipes
    }


async def retrieve_recipe_list() :
    recipes = list(mongodb.engine["ingresync_recipe_data"].find(limit=100))
    for recipe in recipes:
        recipe["_id"] = str(recipe["_id"])
    return recipes


@router.get("/recipe/{recipeid}", response_description="Get a single recipe by rid", response_model=Response)
async def find_recipe(recipeid: str):
    recipe = await retrieve_recipe(recipeid)
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Recipe data retrieved successfully",
        "data": recipe
    }

async def retrieve_recipe(id: str) :
    if (recipe := mongodb.engine["ingresync_recipe_data"].find_one({"recipeid": int(id)})) is not None:
        recipe["_id"] = str(recipe["_id"])
        recipe["ingredients"] = ast.literal_eval(recipe["ingredients"])
        recipe["ingredient_quantity"] = ast.literal_eval(recipe["ingredient_quantity"])
        recipe["process"] = ast.literal_eval(recipe["process"])
        return recipe
    
    return "No such recipe"

@router.post("/login", response_model=Response)
async def check_user(user_name, password):
    user = await check_id_password(user_name, password)
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "User data retrieved successfully",
        "data": user
    }

async def check_id_password(user_name: str, password:str):
    if (user := mongodb.engine["user_login_db"].find_one({"username": user_name})) is not None:
        user["_id"] = str(user["_id"])
        if user["password"] == password:
            user["favorite_category"] = ast.literal_eval(user["favorite_category"])
            user["favorite_food"] = ast.literal_eval(user["favorite_food"])
            return user
    return None

@router.post("/thumbnail/{recipeid}", response_model=Response)
async def post_thumbnail(recipeid):
    thumbnail = retrieve_thumbnail(recipeid)
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Recipe data retrieved successfully",
        "data": thumbnail
    }

async def retrieve_thumbnail(id: str) :
    if (recipe := mongodb.engine["thumbnail_data"].find_one({"recipeid": int(id)})) is not None:
        return recipe["thumbnail_link"]
    
    return "No such recipe"