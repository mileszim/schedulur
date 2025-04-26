from schedulur.models.provider import Provider
from typing import List, Optional
import uuid

# In-memory storage for demo
providers = {}

class ProviderService:
    @staticmethod
    def create_provider(provider: Provider) -> Provider:
        if not provider.id:
            provider.id = str(uuid.uuid4())
        providers[provider.id] = provider
        return provider
    
    @staticmethod
    def get_provider(provider_id: str) -> Optional[Provider]:
        return providers.get(provider_id)
    
    @staticmethod
    def update_provider(provider_id: str, updated_provider: Provider) -> Optional[Provider]:
        if provider_id in providers:
            updated_provider.id = provider_id
            providers[provider_id] = updated_provider
            return updated_provider
        return None
    
    @staticmethod
    def delete_provider(provider_id: str) -> bool:
        if provider_id in providers:
            del providers[provider_id]
            return True
        return False
    
    @staticmethod
    def list_providers() -> List[Provider]:
        return list(providers.values())
    
    @staticmethod
    def filter_providers_by_insurance(insurance_provider: str) -> List[Provider]:
        return [p for p in providers.values() if insurance_provider in p.accepted_insurance]
    
    @staticmethod
    def filter_providers_by_specialization(specialization: str) -> List[Provider]:
        return [p for p in providers.values() if specialization.lower() in p.specialization.lower()]