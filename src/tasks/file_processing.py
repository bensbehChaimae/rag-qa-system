from celery_app import celery_app, get_setup_utils
from helpers.config import get_settings
import asyncio
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemas import DataChunk
from models import ResponseSignal
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers import ProcessController
from controllers import NLPController

import logging
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.file_processing.process_project_files", 
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_project_files(self, project_id: int, 
                          file_id: int, chunk_size: int,
                          overlap_size: int, do_reset: int):

    return asyncio.run(
        _process_project_files(self, project_id, file_id, chunk_size,
                               overlap_size, do_reset)
    )


# Were logic is executed :
async def _process_project_files(task_instance, project_id: int, 
                                 file_id: int, chunk_size: int,
                                 overlap_size: int, do_reset: int):
    

    db_engine, vectordb_client = None, None

    try:
    
        (
                db_engine, db_client, llm_provider_factory, 
                vectordb_provider_factory,
                generation_client, embedding_client, 
                vectordb_client, template_parser) = await get_setup_utils()
        
        # Process function logic before celery integration :
        project_model = await ProjectModel.create_instance(
            db_client= db_client
        )

        project = await project_model.get_project_or_create_one(
            project_id=project_id
        )

        nlp_controller = NLPController(
            vectordb_client=vectordb_client,
            generation_client=generation_client,
            embedding_client=embedding_client,
            template_parser=template_parser,
        )


        asset_model = await AssetModel.create_instance(
            db_client=db_client
        )

        # Get the files : 
        project_files_ids = {}
        if file_id:
            asset_record = await asset_model.get_asset_record(
                asset_project_id= project.project_id ,
                asset_name= file_id
            )

            if asset_record is None : 

                # return JSONResponse(
                #     status_code= status.HTTP_400_BAD_REQUEST,
                #     content={
                #         "signal" : ResponseSignal.FILE_ID_ERROR.value,
                #     }
                # )

                task_instance.update_state(
                            state="FAILURE",
                            meta={
                                "signal": ResponseSignal.FILE_ID_ERROR.value,
                            }
                        )
                
                raise Exception(f"No assets for file: {file_id}")


            project_files_ids = {
                asset_record.asset_id : asset_record.asset_name
            }


        # get the files from the database : 
        else:

            project_files = await asset_model.get_all_project_assets(
                asset_project_id= project.project_id ,
                asset_type= AssetTypeEnum.FILE.value ,
            )

            project_files_ids = {
                record.asset_id : record.asset_name 
                for record in project_files
            }



        if len(project_files_ids) == 0:

            # return JSONResponse(
            #     status_code= status.HTTP_400_BAD_REQUEST,
            #     content={
            #         "signal" : ResponseSignal.NO_FILES_ERROR.value,
            #     }
            # )

            task_instance.update_state(
                    state="FAILURE",
                    meta={
                        "signal": ResponseSignal.NO_FILES_ERROR.value,
                    }
                )

            raise Exception(f"No files found for project_id: {project.project_id}")
        


        process_controller = ProcessController(project_id=project_id)


        num_records =  0 
        num_files = 0

        chunk_model = await ChunkModel.create_instance(
            db_client= db_client
        )

        if do_reset == 1 :
            # delete associated vectors collection
            collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
            _ = await vectordb_client.delete_collection(collection_name=collection_name)

            # delete associated chunks
            _ = await chunk_model.delete_chunks_by_project_id(
                project_id=project.project_id
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

                # return JSONResponse(
                #     status_code=status.HTTP_400_BAD_REQUEST,
                #     content={
                #         "signal" : ResponseSignal.PROCESSING_FAILED.value
                #     }
                # )

                logger.error(f"No chunks for file_id: {file_id}")
                pass


            
            file_chunks_records = [
                DataChunk(
                    chunk_text= chunk.page_content,
                    chunk_metadata = chunk.metadata ,
                    chunk_order = i+1 ,
                    chunk_project_id = project.project_id,
                    chunk_asset_id= asset_id
                )
                for i , chunk in enumerate(file_chunks)
            ] 


            # number of records :
            num_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
            # each time the insertion succeded we add files number 
            num_files += 1



        task_instance.update_state(
                state="SUCCESS",
                meta={
                    "signal": ResponseSignal.PROCESSING_SUCCESS.value,
                }
            )
        
        logger.warning(f"inserted chunks :{num_records}")

        return{

                "signal" : ResponseSignal.PROCESSING_SUCCESS.value,
                "inserted_chunks_num" : num_records,
                "number_of_processed_files" : num_files
        }
    



    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise



    finally:
        try:
            if db_engine:
                await db_engine.dispose()
            
            if vectordb_client:
                await vectordb_client.disconnect()
        except Exception as e:
            logger.error(f"Task failed while cleaning: {str(e)}")





        



