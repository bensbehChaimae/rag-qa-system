from pydantic import BaseModel 
from typing import Optional 


# The schema of the process request :
class ProcessRequest(BaseModel):
    # file_id is now optional
    file_id: str = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0

