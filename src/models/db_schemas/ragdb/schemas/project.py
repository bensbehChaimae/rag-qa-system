from .ragdb_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class Project(SQLAlchemyBase) :
    
    # First thing for SQL Alchemy , table name must be defined :
    __tablename__ = "projects"


    # Define columns names : 
    project_id = Column(Integer, primary_key=True, autoincrement=True)    # primary key (no duplicates) => not ideal to be displayed in business .
    project_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False) 

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


    chunks = relationship("DataChunk", back_populates="project")
    assets = relationship("Asset", back_populates="project")



