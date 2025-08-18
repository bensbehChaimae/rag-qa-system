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
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()
    


    async def resert_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id = project.project_id)
        return await self.vectordb_client.delete_collection(collection_name = collection_name)



    async def get_vector_db_collection_info(self, project: Project):
        
        collection_name = self.create_collection_name(project_id = project.project_id)
       
        collection_info = await self.vectordb_client.get_collection_info(collection_name = collection_name)
        
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    


    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk], 
                             chunks_ids: List[int],
                             do_reset: bool=False):

        # step 1 : get collection name 
        collection_name = self.create_collection_name(project_id = project.project_id)

        # step 2 : manage items 
        texts = [c.chunk_text for c in chunks]
        metadata = [ c.chunk_metadata for c in chunks]
        vectors = self.embedding_client.embed_text(text=texts, 
                                                  document_type=DocumentTypeEnum.DOCUMENT.value)

        # step 3 : create collection if not exist 
        _ = await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )


        # step 4 : insert into vector db 
        _ = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids
        )

        return True 
    


    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 5):

        query_vector = None
        logger.info(f"Searching vector DB for text: {text}") 

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        logger.info(f"Getting collection name")

        # step2: get text embedding vector
        
        try:
            vectors = self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.QUERY.value)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return False

        if not vectors or len(vectors) == 0:
            logger.error("Embedding returned empty vector")
            return False
        
        if isinstance(vectors, list) and len(vectors) > 0:
            query_vector = vectors[0]

        # logger.info(f"Embedding vectors obtained, length={len(vectors)}")

        if not query_vector:
            return False 


        # step3: do semantic search
        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
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
    


    async def answer_rag_question(self, project: Project, query: str, limit: int = 5):

        answer, full_prompt, chat_history = None, None, None
        logger.info(f"[RAG] Starting answer_rag_question for project: {project}, query: '{query}', limit: {limit}")

        # Step 1 : retrieved related documents 
        retrieved_documents = await self.search_vector_db_collection(
            project=project, 
            text=query, 
            limit=limit
        )

        logger.info(f"[RAG] Retrieved {len(retrieved_documents) if retrieved_documents else 0} documents")
        
        # if not retrieved_documents or len(retrieved_documents) == 0 :
        if not retrieved_documents or len(retrieved_documents) == 0  :
            logger.info("[RAG] No documents retrieved or invalid length. Returning None values.")
            return answer, full_prompt, chat_history
        


        # Step 2 : construct LLM prompt 
        system_prompt = self.template_parser.get("rag", "system_prompt")
        logger.info(f"[RAG] System prompt loaded ({len(system_prompt)} chars)")

        # Comprehension list :
        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        logger.info(f"[RAG] Constructed documents_prompts ({len(documents_prompts)} chars)")



        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })
        

        logger.info(f"[RAG] Footer prompt loaded ({len(footer_prompt)} chars)")


        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        logger.info(f"[RAG] Chat history initialized with {len(chat_history)} messages")

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        logger.info(f"[RAG] Full prompt length: {len(full_prompt)} characters")




        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )
    
        print(answer)

        logger.info(f"[RAG] Generated answer length: {len(answer) if answer else 0}")

        return answer, full_prompt, chat_history
    
    





        



    

    
    

        