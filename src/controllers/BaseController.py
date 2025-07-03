from utils.config import Settings , get_settings
import os 
import random 
import string


class BaseController :
    
    def __init__(self):

        self.app_settings = get_settings()

        # Get the path of that file
        self.base_dir = os.path.dirname( os.path.dirname(__file__) )
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )

    ## ------------------------- OPTIONAL ----------------------------------------
    
    # Generate Random name for the files uploaded : 
    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    



