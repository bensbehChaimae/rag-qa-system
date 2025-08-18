from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings) :

    model_config = SettingsConfigDict(env_file=".env")
    # Validation of data : 
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str 

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    # # Mongo Database :
    # MONGODB_URL: str
    # MONGODB_DATABASE: str 

    # LLMs :
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str=None
    OPENAI_API_URL: str=None
    COHERE_API_KEY: str=None

    COHERE_RATE_LIMIT_PER_MINUTE: int=None
    COHERE_MAX_RETRIES: int=None

    GENERATION_MODEL_ID_LITERAL: List[str] = None
    GENRERATION_MODEL_ID: str=None
    EMBEDDING_MODEL_ID: str=None
    EMBEDDING_MODEL_SIZE: int=None

    INPUT_DEFAULT_MAX_CHARACTERS: int=None
    GENERATION_DEFAULT_MAX_TOKENS: int=None
    GENERATION_DEFAULT_TEMPERATURE: float=None

    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str = None

    DEFAULT_LANG: str = "en"
    PRIMAY_LANG: str = "en"

    # Postgres database migration : 
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str


    VECTOR_DB_BACKEND_LITERAL: List[str] = None
    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str = None
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100


    # class Config:
    #     env_file = ".env" 

    

    
def get_settings():
    return Settings()


