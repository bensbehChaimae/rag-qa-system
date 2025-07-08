from fastapi import FastAPI 
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import get_settings



# Define the fastapi app :
app = FastAPI()




# This function runs once when the FastAPI app starts
# It’s used to set up resources like database connections
@app.on_event("startup")
async def startup_db_client():
    # Load application settings (e.g., environment variables)
    settings = get_settings()


    # MongoDB connection

    # Create an asynchronous MongoDB client using Motor
    # This connects to the MongoDB server using the URL from settings   
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    # Access the specific database defined in the settings
    app.db_client =  app.mongo_conn[settings.MONGODB_DATABASE]





# This function runs once when the FastAPI app is shutting down
# It’s used to clean up resources like closing the database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()




app.include_router(base.base_router)
app.include_router(data.data_router)


