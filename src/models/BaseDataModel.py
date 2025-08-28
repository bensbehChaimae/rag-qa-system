# ---------This file defines the base schema/data model class for database operations. ------------------------
# It provides shared functionality and configuration (like DB access and app settings)
# that can be inherited by other data model classes in the project.


from helpers.config import Settings , get_settings




class BaseDataModel:
    
    def __init__(self, db_client: object) :
        self.db_client = db_client
        self.app_settings = get_settings()

