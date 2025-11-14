from config_loader import load_config 

def main(): 
    cfg = load_config() 
    if cfg["DEBUG"]: 
        print("[DEBUG MODE] Verbose logs enabled") 
    print(f"Connecting to DB: {cfg['DB_URL']}") 
    print(f"Using API key: {cfg['API_KEY'][:4]}... (masked)") 

if name == "main": 
    main()