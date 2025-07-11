from fastapi import FastAPI 
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import get_settings
from stores.LLM.LLMProviderFactory import LLMProviderFactory



# Define the fastapi app :
app = FastAPI()


# This function runs once when the FastAPI app starts (used to set up resources like database connections)
# @app.on_event("startup") --> decrepted 
async def startup_db_client():
    # Load application settings 
    settings = get_settings()


    # MongoDB connection
    # Create an asynchronous MongoDB client using Motor
    # This connects to the MongoDB server using the URL from settings   
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    # Access the specific database defined in the settings
    app.db_client =  app.mongo_conn[settings.MONGODB_DATABASE]


    llm_provider_factory = LLMProviderFactory(settings)
    
    # generation client : 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id= settings.GENRERATION_MODEL_ID)

    # embedding client :
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id= settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)






# This function runs once when the FastAPI app is shutting down (used to clean up resources like closing the database connection)
# @app.on_event("shutdown") ---> decrepted 
async def shutdown_db_client():
    app.mongo_conn.close()



# instead of using @ decorator :
app.router.lifespan.on_startup.append(startup_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)


app.include_router(base.base_router)
app.include_router(data.data_router)


