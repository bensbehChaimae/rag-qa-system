APP_NAME=
APP_VERSION=


FILE_ALLOWED_TYPES=["text/plain" , "application/pdf"]
FILE_MAX_SIZE=10
FILE_DEFAULT_CHUNK_SIZE=512000  # 512 KB



# ==================== mongoDB config ===============================================
# # mongodb://username:passwrd@localhost:27007/
# MONGODB_URL=
# MONGODB_DATABASE=



# ==================== Postgres Config ============================================
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
POSTGRES_HOST=              # It was localhost
POSTGRES_PORT=
POSTGRES_MAIN_DATABASE=


# ======================= LLM config ===============================================

GENERATION_BACKEND=
EMBEDDING_BACKEND=


##-------------------- OpenAI LLm --------------------------:
OPENAI_API_KEY=
OPENAI_API_URL=



# ---------------------- Cohere ---------------------------
COHERE_API_KEY=


# --------------------- Generation model ----------------------
GENERATION_MODEL_ID_LITERAL=
GENERATION_MODEL_ID=



# -------------------- Embedding model -------------------------------
EMBEDDING_MODEL_ID=
EMBEDDING_MODEL_SIZE=                             




# 1,42 MIN
INPUT_DEFAULT_MAX_CHARACTERS=1024
GENERATION_DEFAULT_MAX_TOKENS=200
GENERATION_DEFAULT_TEMPERATURE=0.1




# ======================= vector DB config ===============================================
VECTOR_DB_BACKEND_LITERAL=["QDRANT", "PGVECTOR"]
VECTOR_DB_BACKEND="PGVECTOR"
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METHOD="cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD=100






# ======================= Template Configs ===============================================
PRIMARY_LANG="en"
DEFAULT_LANG="en"


# ========================= Celery Task Queue Config =========================
CELERY_BROKER_URL=""  
CELERY_RESULT_BACKEND=""             
CELERY_TASK_SERIALIZER="json"
CELERY_TASK_TIME_LIMIT=600
CELERY_TASK_ACKS_LATE=false                                                  # late acknoweldgment = true
CELERY_WORKER_CONCURRENCY=2
CELERY_FLOWER_PASSWORD=""



COHERE_RATE_LIMIT_PER_MINUTE=90
COHERE_MAX_RETRIES=3