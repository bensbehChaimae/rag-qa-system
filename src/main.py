from fastapi import FastAPI 
from routes import base , data, nlp
# from motor.motor_asyncio import AsyncIOMotorClient  ==> no longer needed to create a connexion to mongoDB
from helpers.config import get_settings
from stores.LLM.LLMProviderFactory import LLMProviderFactory
from stores.vectorDB.VectorDBProviderFactory import VectorDBProviderFactory
from stores.LLM.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import metrics setup
from utils.metrics import setup_metrics


# Define the fastapi app :
app = FastAPI()

# Setup Prometheus metrics
setup_metrics(app)


# This function runs once when the FastAPI app starts (used to set up resources like database connections)
# @app.on_event("startup") --> decrepted 
async def startup_span():
    # Load application settings 
    settings = get_settings()


    # # MongoDB connection --> Create an asynchronous MongoDB client using Motor
    # # This connects to the MongoDB server using the URL from settings   
    # app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    # app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]


    # Postgres connection (migration from mongodb) :
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)

    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )



    
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    
    # generation client : 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id= settings.GENERATION_MODEL_ID)
    

    # embedding client :
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id= settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vector_db client : 
    app.vectordb_client = vectordb_provider_factory.create(
        provider = settings.VECTOR_DB_BACKEND
    )

    await app.vectordb_client.connect()


    # Define a template parser object : 
    app.template_parser = TemplateParser(
        language = settings.PRIMARY_LANG,
        default_language = settings.DEFAULT_LANG,
    )

    





# This function runs once when the FastAPI app is shutting down (used to clean up resources like closing the database connection)
# @app.on_event("shutdown") ---> decrepted 
async def shutdown_span():
    # app.mongo_conn.close()
    app.db_engine.dispose()
    await app.vectordb_client.disconnect()



# instead of using @ decorator :
#app.router.lifespan.on_startup.append(startup_span)
#app.router.lifespan.on_shutdown.append(shutdown_span)
app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)




