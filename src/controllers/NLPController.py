from controllers.BaseController import BaseController
from models.db_schemas import Project, DataChunk
from stores.LLM.LLMEnums import DocumentTypeEnum
from typing import List
import json
import logging # this 


logger = logging.getLogger('uvicorn.error') # this 

class NLPController(BaseController):
    
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):

        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    


    def resert_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id = project.project_id)
        return self.vectordb_client.delete_collection(collection_name = collection_name)



    def get_vector_db_collection_info(self, project: Project):
        
        collection_name = self.create_collection_name(project_id = project.project_id)
       
        collection_info = self.vectordb_client.get_collection_info(collection_name = collection_name)
        
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    


    def index_into_vector_db(self, project: Project, chunks: List[DataChunk], 
                             chunks_ids: List[int],
                             do_reset: bool=False):

        # step 1 : get collection name 
        collection_name = self.create_collection_name(project_id = project.project_id)

        # step 2 : manage items 
        texts = [c.chunk_text for c in chunks]
        metadata = [ c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts 
        ]

        # step 3 : create collection if not exist 
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )


        # step 4 : insert into vector db 
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids
        )

        return True 
    


    def search_vector_db_collection(self, project: Project, text: str, limit: int = 5):

        logger.info(f"Searching vector DB for text: {text}") # this 

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnum.QUERY.value)
        
        try:
            vector = self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.QUERY.value)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return False

        if not vector or len(vector) == 0:
            logger.error("Embedding returned empty vector")
            return False

        logger.info(f"Embedding vector obtained, length={len(vector)}")


        # step3: do semantic search
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        print(results)

        if not results:
            logger.error("VectorDB search returned no results or failed")
            return False
        
        logger.info(f"VectorDB search returned {len(results)} results")

        # return json.loads(
        #     json.dumps(results, default=lambda x: x.__dict__)
        # )
        return results
    


    def answer_rag_question(self, project: Project, query: str, limit: int = 5):

        answer, full_prompt, chat_history = None, None, None

        # Step 1 : retrieved related documents 
        retrieved_documents = self.search_vector_db_collection(
            project=project, 
            text=query, 
            limit=limit
        )
        
        # if not retrieved_documents or len(retrieved_documents) == 0 :
        if not retrieved_documents or len(retrieved_documents) :
            return answer, full_prompt, chat_history
        

        # Step 2 : construct LLM prompt 
        system_prompt = self.template_parser.get("rag", "system_prompt")

        # documents_prompts = []
        # for idx, doc in enumerate(documents_prompts):
        #     documents_prompts.append(
        #         self.template_parser.get("rag", "document_prompt", {
        #             "doc_num": idx+1 ,
        #             "chunk_text": doc.text
        #         })
        #     )

        # Comprehension list :
        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc.text,
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt")


        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])


        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history
    
    





        



    

    
    

        