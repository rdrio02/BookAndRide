import os 
import yaml 
 
def load_config(): 
    env = os.getenv("APP_ENV", "dev").lower() 
    with open("config.yaml", "r") as f: 
        configs = yaml.safe_load(f) 
    if env not in configs: 
        raise ValueError(f"Invalid APP_ENV: {env}. Choose from {list(configs.keys())}") 
    config = configs[env] 
 
    # Normalize types (DEBUG should be boolean) 
    if isinstance(config.get("DEBUG"), str): 
        config["DEBUG"] = config["DEBUG"].lower() == "true" 
 
    return config 
 
if name == "main": 
    cfg = load_config() 
    print("Loaded environment:", os.getenv("APP_ENV", "dev")) 
    print("DB_URL =", cfg["DB_URL"]) 
    print("API_KEY =", cfg["API_KEY"]) 
    print("DEBUG  =", cfg["DEBUG"])