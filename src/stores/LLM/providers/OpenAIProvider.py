from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging
from typing import List, Union

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: str=None ,  
            default_input_max_characters: int=500,
            default_generation_max_output_tokens: int=500,
            default_generation_temperature: float=0.1 ):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens 
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_url if self.api_url and len(self.api_url) else None
        )

        self.enums = OpenAIEnums

        # Define a logger inside a class : 
        self.logger = logging.getLogger(__name__)


    # In runtime : 
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id



    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    # This function was not set on the interface cause some providers won't need it :
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()



    def generate_text(self, prompt: str , chat_history: list=[], max_output_tokens: int=None ,  temperature: float = None) :
        # we are not gonna pass smth toit for now
        # raise NotImplementedError
        if not self.client :
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.generation_model_id :
            self.logger.error("Generation model for OpenAI was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens 
        temperature = temperature if temperature else  self.default_generation_temperature

        # Chat history : 
        chat_history.append(
            self.construct_prompt(prompt = prompt, role = OpenAIEnums.USER.value)
        )
 
        try:
            
            self.logger.info(f"Calling OpenAI model: {self.generation_model_id}")
            self.logger.info(f"Max tokens: {max_output_tokens}, Temperature: {temperature}")
            self.logger.debug(f"Chat history: {chat_history}")

            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                max_tokens=max_output_tokens,
                temperature=temperature
            )

            self.logger.info(f"OpenAI API response received: {type(response)}")

        except Exception as e:
            # print("api url " , self.api_url)
            # print("generation model:", self.generation_model_id)
            self.logger.exception(f"Exception while calling OpenAI API: {e}")
            return None


        # validation :
        if not response or not response.choices or len(response.choices)== 0 or not response.choices[0].message :
            # Avoid logging sensitive user data to protect privacy and comply with security best practices.
            self.logger.error("Error while generating text with OpenAI")
            return None 
        

        return response.choices[0].message.content



    def embed_text(self, text: Union[str, List[str]], document_type: str = None ):
        
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if isinstance(text, str):
            text = [text]
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding :
            self.logger.error("Error while embedding with OpenAI")
            return None
        
        return [ rec.embedding for rec in response.data ]
    


    def construct_prompt(self, prompt: str, role: str):
        return {
            "role" : role ,
            "content" : prompt
        }



    

        








        
         
