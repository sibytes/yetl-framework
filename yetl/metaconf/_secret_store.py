from abc import ABC, abstractmethod

class SecretStore(ABC):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
