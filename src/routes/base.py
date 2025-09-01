from fastapi import FastAPI , APIRouter , Depends
from helpers.config import get_settings, Settings
import logging
from time import sleep
from tasks.mail_service import send_email_reports

logger = logging.getLogger('uvicorn.error')


base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
) 

# Default route : (to check if the app is working)
@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION


    return {
        "app_name" : app_name ,
        "app_version" : app_version      
    }



@base_router.get("/send_reports")
async def send_reports(app_settings: Settings = Depends(get_settings)):

    # ==== START ====== send reports 
    task = send_email_reports.delay(
        mail_wait_seconds=3
    )
    # ===== END ====== send reports

    return {
        "success" : True ,
        "task_id" : task.id
    }
        
