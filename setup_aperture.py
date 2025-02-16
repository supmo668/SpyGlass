import subprocess
import os
from dotenv import load_dotenv

def setup_aperture():
    """Set up ApertureDB configuration."""
    load_dotenv()
    
    # Install ApertureDB Python package
    subprocess.run(["pip", "install", "aperturedb"])
    
    # Create ApertureDB config
    config = {
        "host": os.getenv("APERTUREDB_HOST", "localhost"),
        "port": 55555,
        "username": os.getenv("APERTUREDB_USER", "admin"),
        "password": os.getenv("APERTUREDB_PASSWORD", ""),
        "use_ssl": True,
        "use_rest": False
    }
    
    # Create config directory if it doesn't exist
    config_dir = os.path.expanduser("~/.aperturedb")
    os.makedirs(config_dir, exist_ok=True)
    
    # Write config file
    with open(os.path.join(config_dir, "config.json"), "w") as f:
        import json
        json.dump(config, f, indent=4)
    
    print("ApertureDB configuration created successfully!")
    print("You can now use create_connector() to connect to ApertureDB")

if __name__ == "__main__":
    setup_aperture()
