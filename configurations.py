from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from models import Employee, User, Token
from dotenv import load_dotenv
import os

load_dotenv()
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PWD = os.getenv("MONGODB_PWD")
MONGODB_HOST = os.getenv("MONGODB_HOST")
uri = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PWD}@{MONGODB_HOST}/?retryWrites=true&w=majority&appName=kp-coder"

async def init_db():
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    db = client["employee"]
    await init_beanie(database=db, document_models=[Employee, User, Token])
