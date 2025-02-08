import logging
import os
from dotenv import load_dotenv
from pdf2image import convert_from_path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# local imports
import config
import vectordb
    
    
def extract_text_from_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    logger.debug(f"Loaded {len(pages)} pages from {pdf_path}")
    
    return "\n\n".join([page.page_content.strip() for page in pages])


def process_pdf_files(pdf_dir, chroma_dir, chroma_collection):
    # Loop through all PDF files in the source docs directory
    all_documents = []
    try:
        for file in os.listdir(pdf_dir):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(pdf_dir, file)

            # Load the PDF file in LangChain Document format
            text = extract_text_from_pdf(pdf_path)
            document = Document(page_content=text, metadata={"source": pdf_path})
            
            all_documents.append(document)
            logger.info(f"Loaded {pdf_path} to documents list")
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        raise e
    
    # Vector embed and save the documents to the Chroma DB
    vectordb.ingest_document(chroma_dir, chroma_collection, all_documents, config.CHUNK_SIZE, config.CHUNK_OVERLAP, config.BATCH_SIZE, config.SLEEP_SECONDS)
    logger.info(f"Ingested {len(all_documents)} documents into {chroma_collection}")
            
            
if __name__ == "__main__":
    # Load secrets and other environment variables
    load_dotenv()

    # Read config
    config = config.read_config()
    print(f"Ingesting documents for {config['topic']} into {config['chroma_collection']}")
    print(f"Source docs: {config['pdf_base_dir']}")
    print(f"Chroma DB: {config['chroma_base_dir']}")
    logging.basicConfig(level=config['LOG_LEVEL'])
    logger = logging.getLogger(__name__)

    # Ingest documents
    pdf_dir = os.path.join(config['pdf_base_dir'], config['chroma_collection'])
    chroma_dir = os.path.join(config['chroma_base_dir'], config['chroma_collection'])
    process_pdf_files(pdf_dir, chroma_dir, config['chroma_collection'])

