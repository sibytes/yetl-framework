from datetime import datetime
from typing import List, Optional
from ._secret_store import SecretStore

class Environment():
    
    environment: str
    project: str
    secret_store: SecretStore

