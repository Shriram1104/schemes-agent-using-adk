"""
Configuration settings - Simple version that accepts all env vars
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Simple settings class that doesn't validate extra fields"""
    
    def __init__(self):
        # GCP
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID", "")
        self.gcp_location = os.getenv("GCP_LOCATION", "global")
        
        # API Keys (won't cause validation errors)
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        
        # Datastores
        self.farmer_datastore_id = os.getenv("FARMER_DATASTORE_ID", "")
        self.msme_datastore_id = os.getenv("MSME_DATASTORE_ID", "")
        
        # Model
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Pagination
        self.schemes_per_page = int(os.getenv("SCHEMES_PER_PAGE", "3"))
        
        # Mock mode
        self.use_mock_search = os.getenv("USE_MOCK_SEARCH", "false").lower() == "true"

settings = Settings()

# Debug print
print(f"⚙️  Settings loaded successfully")
print(f"   GCP Project: {settings.gcp_project_id}")
print(f"   Mock Mode: {settings.use_mock_search}")
print(f"   Farmer Datastore: {settings.farmer_datastore_id[:50]}..." if settings.farmer_datastore_id else "   Farmer Datastore: Not set")