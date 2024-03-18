from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI
import json
import sys
from config import Config
from utils.rag_utils import truncate_text_tokens, num_tokens_from_string, EMBEDDING_CTX_LENGTH

class DocumentationEmbedding:
    def __init__(self, collection_name, json_dataset_file_path, vector_size=1536) -> None:
        # self.vectordb_client = self.create_vectordb_client(is_testing=True, vectordb_provider='qdrant')
        self.vector_size = vector_size

        self.collection_name = collection_name
        # self.all_collections = self.vectordb_client.get_collections()

        # if collection_name not in self.all_collections:
        #     print (f"Collection {collection_name} does not exists. Creating a new collection...")
        #     self.vectordb_client.create_collection(
        #         collection_name=collection_name,
        #         vectors_config = {
        #             "example_code": models.VectorParams(
        #                 distance=models.Distance.COSINE,
        #                 size=self.vector_size,
        #             )
        #         }
        #     )

        #     print (f"New collection with the name {collection_name} created\n")
        
        self.json_dataset_file_path = json_dataset_file_path
        
        try:
            with open(json_dataset_file_path, "r") as file:
                print (f"Dataset at path {json_dataset_file_path} loading...")
                self.json_dataset = json.load(file)
                print (f"Loaded successfully.")
                print (f"Total records loaded: {len(self.json_dataset)}")

        except Exception as e:
            print (f"Dataset at path {json_dataset_file_path} could not be loaded successfully.\nError: {e}")
            self.json_dataset = None

        # if self.json_dataset:        
        #     for record in self.json_dataset:
        #         print (record.keys())
            
        #     print (f"Total records processed: {len(self.json_dataset)}")


    def create_vectordb_client(self, is_testing: bool, vectordb_provider: str):

        if vectordb_provider == "qdrant":
            try:
                if is_testing:
                    vectordb_client = QdrantClient(
                        host='localhost',
                        port=6333
                    )

                    print ("Connecting to Qdrant local instance...")

                else:
                    vectordb_client = QdrantClient(
                        url=Config.QDRANT_DB_URL, 
                        api_key=Config.QDRANT_CLOUD_KEY,
                    )
                    
                    print ("Connecting to Qdrant cloud instance...")

                print ('Connected successfully.')
                return vectordb_client

            except Exception as e:
                print(f"Failed to create or use Qdrant client: {e}", file=sys.stderr)
        else:
            raise ValueError(f"{vectordb_provider} vectordb provider currently not supported. Please use Qdrant vector db.")

    def __text2embedding(text: str):
        pass

    def __code2embedding(text: str):
        # first check how many tokens does the content correspond to
        num_tokens = num_tokens_from_string(text)
        
        # truncate input string if the number of tokens exceed maximum context length
        if num_tokens > EMBEDDING_CTX_LENGTH:
            print (f"Input string contain {num_tokens} tokens that exceeds token limit of {EMBEDDING_CTX_LENGTH}.")
            print ("Truncating the string..")
            text = truncate_text_tokens(text=text)

        # initialize OpenAI client
        client = OpenAI()

        # generate embeddings using OpenAI Embeddings endpoint
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )

        return response.data[0].embedding


    def create_and_save_embeddings_in_qdrant(self):
        """
            1. Iterate over all each record in the JSON dataset
                - Create vector embeddings for the markdown/text fields
                - Also add metadata in payload
            2. Save all the records as Points in Qdrant DB
        """
        qdrant_json_dataset = []
        for i, record in enumerate(self.json_dataset[1:2]):
            print (f"Index: {i}")
            # create embedding for the record['markdown'] field
            print (f"\t1. Markdown: \n\t\t{record['markdown']}")
            print (f"\t2. URL: {record['url']}")
            print (f"\t3. Metadata:")
            print (f"\t\t- ReferrerURL: {record['crawl']['referrerUrl']}")
            print (f"\t\t- Page title: {record['metadata']['title']}")
            print (f"\t\t- Page description: {record['metadata']['description']}")

            print ("--"*50)

            # add payload
            #   - title
            #   - url
            #   - parentUrl

        
        # Save qdrant_json_dataset in qdrant vector db

if __name__ == "__main__":
    doc_embedding = DocumentationEmbedding(
                            collection_name="TestDB",
                            json_dataset_file_path="datasets/dataset_trigger-dev-examples_2024-03-16_13-56-52-250.json"
                    )
    
    doc_embedding.create_and_save_embeddings_in_qdrant()