from fastapi import FastAPI , APIRouter , Depends , UploadFile, status, Request
from fastapi.responses import JSONResponse
import os 
from utils.config import get_settings , Settings 
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

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1" , "data"]
)


# Define the upload endpoint :
@data_router.post("/upload/{project_id}") 
async def upload_data(request: Request , project_id: str, file: UploadFile , 
                      app_settings: Settings = Depends(get_settings)):
    

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client

    )

    project = await project_model.get_project_or_create_one(
        project_id = project_id
    )


    # Validate the file properties : 
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid : 
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "signal" : result_signal
            }
        )

    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    file_path, file_id = data_controller.generate_unique_filepath(
        original_file_name= file.filename ,
        project_id= project_id 
    )


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
        asset_project_id= project.id,
        asset_type= AssetTypeEnum.FILE.value,
        asset_name= file_id,
        asset_size= os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
            content = {
                "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.id)
            }
        )



# Define the process endpoint 
@data_router.post("/process/{project_id}") 
async def process_endpoint(request: Request, project_id: str , process_request: ProcessRequest):

    # process_request from routes/schemas/data.py that define the schema of data loaded
    # file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset



    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )


    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    # Get the files : 
    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id= project.id ,
            asset_name= process_request.file_id
        )

        if asset_record is None : 
            return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseSignal.FILE_ID_ERROR.value,
                }
            )


        project_files_ids = {
            asset_record.id : asset_record.asset_name
        }


    # get the files from the database : 
    else:

        project_files = await asset_model.get_all_project_assets(
            asset_project_id= project.id ,
            asset_type= AssetTypeEnum.FILE.value ,
        )

        project_files_ids = {
            record.id : record.asset_name 
            for record in project_files
        }



    if len(project_files_ids) == 0:

        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal" : ResponseSignal.NO_FILES_ERROR.value,
            }
        )




    process_controller = ProcessController(project_id=project_id)


    num_records =  0 
    num_files = 0

    chunk_model = await ChunkModel.create_instance(
        db_client= request.app.db_client
    )

    if do_reset == 1 :
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id = project.id
        )

    for asset_id , file_id in project_files_ids.items() :

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None :
            logger.error(f"Error while processing the file: {file_id}")
            continue 

        file_chunks = process_controller.process_file_content( 
            file_content=file_content, 
            file_id=file_id ,
            chunk_size=chunk_size,
            overlap_size=overlap_size                                                 
        )

        if file_chunks is None or len(file_chunks) == 0 :
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseSignal.PROCESSING_FAILED.value
                }
            )
        
        file_chunks_records = [
            DataChunk(
                chunk_text= chunk.page_content,
                chunk_metadata = chunk.metadata ,
                chunk_order = i+1 ,
                chunk_project_id = project.id,
                chunk_asset_id= asset_id
            )
            for i , chunk in enumerate(file_chunks)
        ] 


        # number of records :
        num_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        # each time the insertion succeded we add files number 
        num_files += 1





    return JSONResponse(
        content={
            "signal" : ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks_num" : num_records,
            "number_of_processed_files" : num_files
        }
    )












    


