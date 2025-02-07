import json
import logging
import os
import time
from dotenv import load_dotenv
from pdf2image import convert_from_path
import pytesseract

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def read_config():
    with open("./hello-world/config.json", "r") as f:
        config = json.load(f)
    
        topic = config["topic"]
        chroma_collection = config["chroma_collection"]
        pdf_base_dir = config["pdf_base_dir"]
        chroma_base_dir = config["chroma_base_dir"]

        return topic, chroma_collection, pdf_base_dir, chroma_base_dir
    
def extract_text_and_ocr_from_pdf(pdf_path, dpi=300, lang="eng"):
    """
    Extract text and OCR from a PDF file using BOTH a standard text loader (PyPDFLoader)
    and OCR (pytesseract) for images. Merges the results for each page..
    """
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    logging.debug(f"Loaded {len(pages)} pages from {pdf_path}")

    # Convert entire PDF to images (one per page)    
    images = convert_from_path(pdf_path, dpi=dpi)
    logging.debug(f"Converted PDF to {len(images)} images")
    
    if len(pages) != len(images):
        print(f"Warning: Number of pages in PDF ({len(pages)}) does not match number of images ({len(images)})")
        
    merged_page_texts = []
    num_pages = max(len(pages), len(images))
    
    for page_idx in range(num_pages):
        # Text from PDF parser (if within index)
        pdf_text = ""
        if (page_idx < len(pages)):
            pdf_text = pages[page_idx].page_content.strip() if pages[page_idx].page_content else ""
            
        # OCR text from image
        ocr_text = ""
        if (page_idx < len(images)):
            ocr_text = pytesseract.image_to_string(images[page_idx], lang=lang).strip()
            
        # If the PDF layer has text, we keep it
        # If the OCR finds additional text, we append it (unless it's a near-duplicate)
        combined_text = pdf_text
        
        # Hueristic: Only append OCR text if it adds something beyone pdf_text
        # You can do more advanced deduplication or fuzzy matching here.
        if ocr_text and ocr_text not in pdf_text:
            # Possibly separate with a delimiter or label it as "OCR text"
            combined_text += f"\n[OCR TEXT]\n{ocr_text}"
            
        merged_page_texts.append(combined_text)
        
    # At this point, merged_page_texts is a list of text strings, one per page
    # We'll combine them or keep them separate as needed
    logging.debug(f"Merged pages into {len(merged_page_texts)} texts")
    
    # Example: combine into one big string
    full_merged_text = "\n\n".join(merged_page_texts)
    logging.debug(f"Full merged text length: {len(full_merged_text)}")
    
    return full_merged_text
         
def extract_text_from_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    logging.debug(f"Loaded {len(pages)} pages from {pdf_path}")
    
    return "\n\n".join([page.page_content.strip() for page in pages])

def ingest_documents(pdf_dir, chroma_dir, chroma_collection):
    # 1. Initialize embeddings and Chroma vector store
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Load existing collection if it exists, otherwise create a new one
    vector_store = Chroma(
        collection_name=chroma_collection,
        embedding_function=embeddings,
        persist_directory=chroma_dir
    )
    
    # 2. Create a text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    # 3. Loop through all PDF files in the source docs directory
    all_chunks = []
    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, file)
            print(f"Ingesting: {pdf_path}") 

            # 4. Load the PDF file
            # text = extract_text_and_ocr_from_pdf(pdf_path)
            text = extract_text_from_pdf(pdf_path)
            print(f"Text size: {len(text)}")
            document = Document(page_content=text, metadata={"source": pdf_path})
            
            # 5. Split the document into chunks
            chunks = text_splitter.split_documents([document])
            print(f"Number of chunks: {len(chunks)}")
            all_chunks.extend(chunks)
            
    # 6. Add the chunks to the vector store
    BATCH_SIZE = 100
    SLEEP_SECONDS = 1
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i:i+BATCH_SIZE]
        vector_store.add_documents(batch)
        print(f"Added {len(batch)} chunks to the vector store")
        time.sleep(SLEEP_SECONDS)
            
    # 7. Persist the vector store to disk
    vector_store.persist()
    print(f"Documents ingested and saved to {chroma_dir}")
            
            
if __name__ == "__main__":
    # Load secrets and other environment variables
    load_dotenv()

    # Read config
    topic, chroma_collection, pdf_base_dir, chroma_base_dir = read_config()
    print(f"Ingesting documents for {topic} into {chroma_collection}")
    print(f"Source docs: {pdf_base_dir}")
    print(f"Chroma DB: {chroma_base_dir}")

    # Ingest documents
    pdf_dir = os.path.join(pdf_base_dir, chroma_collection)
    chroma_dir = os.path.join(chroma_base_dir, chroma_collection)
    ingest_documents(pdf_dir, chroma_dir, chroma_collection)

