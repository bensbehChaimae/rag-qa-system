from fastapi import FastAPI , APIRouter , Depends , UploadFile, status, Request, File
from fastapi.responses import JSONResponse
import os 
from helpers.config import get_settings , Settings 
# from controllers.DataController import DataController
from controllers import DataController, ProjectController, ProcessController

import aiofiles
from models import ResponseSignal 
import logging
# Define a logging object 
logger = logging.getLogger('uvicorn.error')


from routes.schemas.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemas import DataChunk
from models.AssetModel import AssetModel, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
from bson import ObjectId
from controllers import NLPController
from tasks.file_processing import process_project_files
from tasks.process_workflow import process_and_push_workflow



data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1" , "data"]
)


# Define the upload endpoint :
@data_router.post("/upload/{project_id}") 
# project_id :int 
async def upload_data(request: Request , project_id: int, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)): 
    
    logger.info(f"Starting upload document :")
    

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    logger.info(f"getting project model")


    
    project = await project_model.get_project_or_create_one(project_id=project_id)


    logger.info(f"getting project")


    # Validate the file properties : 
    data_controller = DataController()

    logger.info(f"data controller")

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    logger.info(f"validate uploaded file")

    if not is_valid : 
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "signal" : result_signal
            }
        )
    
    logger.info(f"file validate success")

    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    logger.info(f"project dir path")

    file_path, file_id = data_controller.generate_unique_filepath(
        original_file_name= file.filename ,
        project_id= project_id 
    )

    logger.info(f"file path, file_id")

    # error hereeeee ....................
    
    try :  
        async with aiofiles.open(file_path , "wb") as f :
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e :
        # Info user will not see :
        logger.error(f"Error while uploading file: {e}")
        
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "signal" : ResponseSignal.FILE_UPLOAD_FAIL.value
            }
        )



    # Store the asset into the database :
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    # Create asset : 
    asset_resource = Asset(
        asset_project_id= project.project_id,  # this project.id
        asset_type= AssetTypeEnum.FILE.value,
        asset_name= file_id,
        asset_size= os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
            content = {
                "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.asset_id)           # asset_record.id
            }
        )



# Define the process endpoint :
@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    task = process_project_files.delay(
        project_id=project_id,
        file_id=process_request.file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset,
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "task_id": task.id
        }
    )



# Define the process and push celery tasks endpoint : 
@data_router.post("/process-and-push/{project_id}") 
async def process_and_push_endpoint(request: Request, project_id: int, process_request: ProcessRequest):

    # process_request from routes/schemas/data.py that define the schema of data loaded
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    # Define the celery task : 
    workflow_task = process_and_push_workflow.delay(
        project_id=project_id,
        file_id=process_request.file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset,
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESS_AND_PUSH_WORKFLOW_READY.value,
            "workflow_task_id": workflow_task.id
        }
    )




    












    


