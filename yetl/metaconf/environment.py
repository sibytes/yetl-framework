from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from .secret_store import SecretStore

class Environment(BaseModel):
    
    environment: str
    project: str
    secret_store: SecretStore

