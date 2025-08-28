FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm        


WORKDIR /app


# Install additional system dependencies for lxml and other packages before installing requirements 
RUN apt-get update && apt-get install -y \
    build-essential \
    libavif-dev pkg-config \
    libjpeg-dev \
    libpq-dev \
    gcc unzip zip \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements on /app
COPY src/requirements.txt .


# Install requirements 
RUN uv pip install -r requirements.txt --system


# Copy application source code 
COPY src/ .


# ===== Alembic set up =====
# Create directory structure for Alembic 
RUN mkdir -p /app/models/db_schemas/ragdb/


COPY docker/ragdb/alembic.ini /app/models/db_schemas/ragdb/alembic.ini


COPY docker/ragdb/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]



# Command to run the application
# uvicorn main:app --reload --host 0.0.0.0 --port 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

