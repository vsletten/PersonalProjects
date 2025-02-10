import os
import time

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

def ingest_documents(chroma_dir, chroma_collection, documents, chunk_size, chunk_overlap, BATCH_SIZE, SLEEP_SECONDS):
    """
    Vector embed and save a list of documents into the vector database.
    """
    try:
        # Get embedding model
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        raise e

    try:
        # Initialize Chroma DB vector store, passing it the embedding model
        vector_store = Chroma(
            collection_name=chroma_collection,
            embedding_function=embeddings,
            persist_directory=chroma_dir
        )
    except Exception as e:
        print(f"Error opening vector store: {e}")
        raise e
    
    try:    
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
        chunks = text_splitter.split_documents(documents)
    except Exception as e:
        print(f"Error splitting documents: {e}")
        raise e

    # Add all of the chunks to the Chroma Db collection. The chunks are embedded 
    # during ingestion, using the embedding model supplied during vector store initialization.    
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i+BATCH_SIZE]
        vector_store.add_documents(batch)
        time.sleep(SLEEP_SECONDS)
            
    vector_store.persist()

    

