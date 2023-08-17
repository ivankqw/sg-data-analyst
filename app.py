from pprint import pprint
from typing import List, Tuple, Dict, Any
import openai
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
import asyncio
from datagov import aget_csv_datasets, get_datasets_from_ids
from definitions.dataset import Dataset
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from ast import literal_eval


GPT_MODEL: str = "gpt-3.5-turbo-16k-0613"
_ = load_dotenv(find_dotenv())

query = "How many students were working part-time in 2019?"

loop = asyncio.get_event_loop()

csv_datasets: List[Dataset] = loop.run_until_complete(
    aget_csv_datasets()
)
print(f"Obtained {len(csv_datasets)} datasets.")

dataset_docs = [dataset.to_document() for dataset in csv_datasets]

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
print(f"splitting and embedding {len(dataset_docs)} documents.")
dataset_split_docs = text_splitter.split_documents(dataset_docs)
print(f"loading split documents into vector store.")
db = FAISS.from_documents(dataset_docs, OpenAIEmbeddings())
print(f"loaded documents into vector store!")
fetched_docs = db.similarity_search(query)


q = f"""Given that you know the following datasets with information given in triple backticks:
```
{fetched_docs}
```

Retrieve the relevant datasets that can answer the following query given in triple backticks. If there are no relevant datasets, return an empty list.:
```
{query}
```
"""

messages = []
messages.append({"role": "user", "content": q})

functions = [
    {
        "name": "get_datasets_from_ids",
        "description": "Get the datasets from the ids",
        "parameters": {
            "type": "object",
            "properties": {
                "ids": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "The ids of the datasets",
                    },
                },
            },
            "required": ["ids"],
        },
    },
]

# TODO: refactor all these out into another file
# get function inputs using openai once, forcefully
try:
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        functions=functions,
        function_call={"name": "get_datasets_from_ids"},
        temperature=0,
    )
except openai.error.OpenAIError:
    # TODO: implement a retry mechanism
    pass

try:
    ids_raw = response["choices"][0]["message"]["function_call"]["arguments"]
    # then parse the arguments
    ids_dict = literal_eval(ids_raw)
    ids = ids_dict["ids"]
except KeyError:
    print("Could not retrieve ids.")
    ids = []


if __name__ == "__main__":
    print(ids)
