from asyncio import current_task
from fastapi import FastAPI
from app.routes import router as recipe_router

from app.models import mongodb

app = FastAPI()


@app.on_event("startup")
def on_app_start():
	mongodb.connect()

@app.on_event("shutdown")
async def on_app_shutdown():
	mongodb.close()

app.include_router(recipe_router, )