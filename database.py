# database.py
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("db.env")

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(
	MONGO_URI,
	tls=True,
	tlsCAFile=certifi.where(),
	serverSelectionTimeoutMS=10000,
)
db = client[DB_NAME]
reports_collection = db.get_collection("reports")