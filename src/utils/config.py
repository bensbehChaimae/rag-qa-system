from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings) :

    model_config = SettingsConfigDict(env_file=".env")
    # Validation of data : 
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str 

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    # Database :
    MONGODB_URL: str
    MONGODB_DATABASE: str 

    # LLMs :
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str=None
    OPENAI_API_URL: str=None
    COHERE_API_KEY: str=None

    COHERE_RATE_LIMIT_PER_MINUTE: int=None
    COHERE_MAX_RETRIES: int=None

    GENRERATION_MODEL_ID: str=None
    EMBEDDING_MODEL_ID: str=None
    EMBEDDING_MODEL_SIZE: int=None

    INPUT_DEFAULT_MAX_CHARACTERS: int=None
    GENERATION_DEFAULT_MAX_TOKENS: int=None
    GENERATION_DEFAULT_TEMPERATURE: float=None

    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str = None





    
def get_settings():
    return Settings()


