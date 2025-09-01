from enum import Enum

# ResponseSignal inherit from Enum :
class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "File validated successfully"

    FILE_TYPE_NOTE_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeded"
    FILE_UPLOAD_SUCCESS = "File upload success"
    FILE_UPLOAD_FAIL = "File upload fail"

    PROCESSING_FAILED = "File processing failed"
    PROCESSING_SUCCESS = "File processing success"

    NO_FILES_ERROR = "not found files"
    FILE_ID_ERROR = "no file found with this id"

    PROJECT_NOT_FOUND_ERROR = "project not found"

    INSERT_INTO_VECTORDB_ERROR = "insert into vectorDB error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert into vectorDB success"
    VECTORDB_COLLECTION_RETRIEVED = "vectorDB collection retrieved"
    VECTORDB_SEARCH_ERROR = "vectorDB search error"
    VECTORDB_SEARCH_SUCCESS = "vectorDB search success"

    RAG_ANSWER_ERROR = "rag answer error"
    RAG_ANSWER_SUCCESS = "rag answer success"

    DATA_PUSH_TASK_READY = "data push task ready"
    PROCESS_AND_PUSH_WORKFLOW_READY = "process and push workflow ready"
    







