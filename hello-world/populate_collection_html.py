import os
import chromadb
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# local imports
import config

def load_html_content(dir_path):
    """
    Reads and concatenates all HTML files in the given directory.
    """
    full_text = ""
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".html") or file.endswith(".htm"):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    text = soup.get_text(separator=" ", strip=True)
                    full_text += text + "\n"

    return full_text.strip()

def embed_text(text):
    """
    Generates vector embeddings for the given text using OpenAI's embedding API.
    """
    response = openai.embeddings.create(text=text, model="text-embedding-3-small")
    return response["data"][0]["embedding"]

def store_in_chromadb(client, chroma_collection, doc_id, text, embedding):
    """
    Stores the embedding in the ChromaDB collection.
    """
    collection = client.get_or_create_collection(chroma_collection)
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        metadatas=[{"source": doc_id}],
        documents=[text]
    )

def process_websites(source_dir, chroma_base_dir, chroma_collection):
    """
    Process all HTML files in the source directory and add them to the Chroma vector store.
    """
    client = chromadb.Client(path=chroma_base_dir)
    full_text = ""
    for current_dir in os.listdir(source_dir):
        current_dir_path = os.path.join(source_dir, current_dir)
        if (os.path.isdir(current_dir_path)):
            print(f"Processing website: {current_dir}")
            text = load_html_content(current_dir_path)
            if text:
                full_text += text
                print(f"Stored {current_dir} in Chroma DB")
            else:
                print(f"Skipping {current_dir} because it has no text")
        else:
            print(f"{current_dir} is not a directory")
            
    if full_text:
        embedding = embed_text(full_text)
        store_in_chromadb(client, chroma_collection, source_dir, full_text, embedding)


def main():
    load_dotenv()
    config = config.read_config()
    process_websites(config["html_base_dir"], config["chroma_base_dir"], config["chroma_collection"])
    print("Processing complete")

if __name__ == "__main__":
    main()