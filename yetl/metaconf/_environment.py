
class Environment():

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    # def __init__(self, name:str, project:str, secrets:) -> None:
        