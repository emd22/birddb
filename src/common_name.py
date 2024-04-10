from utils import sanitize

class CommonName:
    def __init__(self, id: str, name: str):
        self.id = id                # this is our taxonID!
        self.name = sanitize(name)  # sqeaky clean

    def __str__(self) -> str:
        return f'{self.id} || {self.name}'
