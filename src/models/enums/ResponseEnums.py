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





