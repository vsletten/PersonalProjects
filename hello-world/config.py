import json

def read_config():
    with open("./hello-world/config.json", "r") as f:
        config = json.load(f)
    
        topic = config["topic"]
        chroma_collection = config["chroma_collection"]
        pdf_base_dir = config["pdf_base_dir"]
        chroma_base_dir = config["chroma_base_dir"]

        return topic, chroma_collection, pdf_base_dir, chroma_base_dir
