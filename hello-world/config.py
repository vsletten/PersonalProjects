import json

def read_config():
    with open("./hello-world/config.json", "r") as f:
        config = json.load(f)
    
    return config