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

    MONGODB_URL: str
    MONGODB_DATABASE: str 

    
def get_settings():
    return Settings()


