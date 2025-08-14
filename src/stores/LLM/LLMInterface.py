# In python to design an interface we need to import a python package *abc*
from abc import ABC, abstractmethod


# Interface: defines the structure of a class (its methods and properties) without providing the implementation.

# In most models, the component that handles embedding is different from the one that handles generation.

# Decorator: uses @ syntax to modify or enhance the behavior of a function without changing its actual code.

class LLMInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass 


    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        pass 


    @abstractmethod
    # Temperature parameter: The closer it is to 0, the model becomes more deterministic—it generates less creative responses and sticks more to factual and predictable outputs.
    def generate_text(self, prompt: str , chat_history: list=[], max_output_tokens: int=None ,  temperature: float = None):
        pass 


    @abstractmethod
    # input = text -> ouput = vector 
    def embed_text(self, text: str, document_type: str = None ):
        pass 


    @abstractmethod
    # prompt ---> (llm provider) ---> 
    def construct_prompt(self, prompt: str, role: str):
        pass 



