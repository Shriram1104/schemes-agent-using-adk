"""
Vertex AI Search Service with correct schema mapping
"""
from google.cloud import discoveryengine_v1 as discoveryengine
from typing import List, Optional
from src.models.schemas import Scheme
from config.settings import settings
import os

class VertexSearchService:
    def __init__(self, datastore_path: str):
        """
        Initialize with datastore path but don't create client yet
        
        datastore_path: Full path like 
        projects/{PROJECT}/locations/{LOCATION}/collections/default_collection/dataStores/{DATASTORE_ID}
        """
        self.datastore_path = datastore_path
        self._client: Optional[discoveryengine.SearchServiceClient] = None
        self.serving_config = f"{datastore_path}/servingConfigs/default_config"
    
    @property
    def client(self):
        """Lazy initialization of the client"""
        if self._client is None:
            # Check for credentials
            if not self._check_credentials():
                raise RuntimeError(
                    "Google Cloud credentials not found. Please run:\n"
                    "  gcloud auth application-default login\n"
                    "Or set GOOGLE_APPLICATION_CREDENTIALS environment variable"
                )
            self._client = discoveryengine.SearchServiceClient()
        return self._client
    
    def _check_credentials(self) -> bool:
        """Check if Google Cloud credentials are available"""
        # Check for service account key file
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return os.path.exists(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        
        # Check for gcloud auth
        import subprocess
        try:
            result = subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def search(self, query: str, top_k: int = 10) -> List[Scheme]:
        """Search the vertex AI datastore and return schemes"""
        request = discoveryengine.SearchRequest(
            serving_config=self.serving_config,
            query=query,
            page_size=top_k,
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
        )
        
        try:
            response = self.client.search(request)
            schemes = []
            
            for result in response.results:
                doc = result.document
                struct_data = doc.struct_data if hasattr(doc, 'struct_data') else {}
                
                # Your schema has data at root with nested 'data' object
                data_obj = struct_data.get('data', {})
                if hasattr(data_obj, 'items'):
                    data_dict = dict(data_obj)
                else:
                    data_dict = data_obj if isinstance(data_obj, dict) else {}
                
                # Helper to safely get values
                def get_value(obj, key, default=""):
                    """Safely get value from dict or proto object"""
                    if not obj:
                        return default
                    try:
                        if hasattr(obj, 'get'):
                            val = obj.get(key, default)
                        elif hasattr(obj, key):
                            val = getattr(obj, key, default)
                        else:
                            return default
                        return str(val) if val else default
                    except:
                        return default
                
                # Extract fields according to your schema
                name = get_value(data_dict, 'name', 'Untitled Scheme')
                description = get_value(data_dict, 'description', 'No description available')
                eligibility = get_value(data_dict, 'eligibility', 'Contact office for details')
                
                # benefitSummary is a string field
                benefits = get_value(data_dict, 'benefitSummary', '')
                
                # If benefitSummary is empty, try to get from benefit object
                if not benefits:
                    benefit_obj = data_dict.get('benefit', {})
                    if benefit_obj and hasattr(benefit_obj, 'items'):
                        benefit_dict = dict(benefit_obj)
                        # Try common benefit field names
                        benefits = (get_value(benefit_dict, 'description', '') or 
                                  get_value(benefit_dict, 'summary', '') or
                                  get_value(benefit_dict, 'details', ''))
                
                # Process is a string field
                application_process = get_value(data_dict, 'process', '')
                
                # Get department/agency info
                dept = get_value(data_dict, 'departmentAgency', '')
                
                # Try to construct URL from available data
                scheme_type = get_value(data_dict, 'schemeType', '')
                guid = get_value(data_dict, 'guid', '')
                url = ""  # Your schema doesn't have URL field
                
                # If we have guid, we could construct a URL (modify as needed)
                if guid:
                    url = f"https://schemes.gov.in/scheme/{guid}"  # Example URL
                
                scheme = Scheme(
                    id=doc.id,
                    name=name,
                    description=description,
                    eligibility=eligibility,
                    benefits=benefits,
                    application_process=application_process if application_process else f"Contact {dept}" if dept else "",
                    url=url,
                )
                
                # Skip metadata/index documents (no real scheme data)
                if name == "Untitled Scheme" or not description or description == "No description available":
                    print(f"   ⏭️  Skipping metadata document: {doc.id}")
                    continue
                
                schemes.append(scheme)
            
            if schemes:
                print(f"✅ Retrieved {len(schemes)} schemes")
                if schemes[0].name != "Untitled Scheme":
                    print(f"   First scheme: {schemes[0].name[:50]}...")
            
            return schemes
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            import traceback
            traceback.print_exc()
            return []