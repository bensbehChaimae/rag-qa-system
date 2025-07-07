from pydantic import BaseModel, Field,  validator
from typing import Optional
from bson.objectid import ObjectId



class Project(BaseModel):

    # The MongoDB document's unique identifier
    # We don't provide _id when creating a new document — MongoDB generates it automatically
    # After insertion, the document will include this _id field
    _id: Optional[ObjectId]

    # The project_id is a required field (cannot be missing or empty)
    # It must be a string with at least one character
    project_id: str = Field(... , min_length=1)

    # Design a custom validation on the schema :
    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value
    

    # but pydantic doesn't know ObjectId :
    # tell pydantic to ignore it 
    class Config:
        arbitrary_types_allowed = True