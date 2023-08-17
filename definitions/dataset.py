from dataclasses import dataclass
from langchain.schema import Document


@dataclass
class Dataset:
    """Dataset class to store dataset information"""
    id: str
    name: str
    description: str

    def __repr__(self):
        return f"""Dataset(
    id={self.id},
    name={self.name},
    description={self.description})
    """

    def to_document(self):
        return Document(page_content=self.__repr__())
