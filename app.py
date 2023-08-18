from openai_functions import generate_id_choices
from typing import List
from dotenv import load_dotenv, find_dotenv
import asyncio
from datagov import aget_csv_datasets, aget_datasets_from_ids
from definitions.dataset import Dataset
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import time

_ = load_dotenv(find_dotenv())

query = "How many students were working part-time in 2019?"

start = time.time()

loop = asyncio.get_event_loop()

csv_datasets: List[Dataset] = loop.run_until_complete(
    aget_csv_datasets()
)
# TODO: also a bottleneck, need to find a way to speed this up (8 seconds)
print(
    f"Obtained {len(csv_datasets)} datasets in {time.time() - start} seconds.")

dataset_docs = [dataset.to_document() for dataset in csv_datasets]
# put them into a dictionary as well for easy access
dataset_docs_dict = {dataset.id: dataset for dataset in csv_datasets}

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
print(f"splitting and embedding {len(dataset_docs)} documents.")
dataset_split_docs = text_splitter.split_documents(dataset_docs)
print(f"loading split documents into vector store.")
start = time.time()
db = FAISS.from_documents(dataset_docs, OpenAIEmbeddings())
# TODO: this is the bottleneck, need to find a way to speed this up (16 seconds)
print(f"loaded documents into vector store in {time.time() - start} seconds.")
fetched_docs = db.similarity_search(query)
print(f"found {len(fetched_docs)} candidate documents.")
print(f"top 5 documents that match the query {query}: {fetched_docs[:5]}")

# get the most relevant ids from the fetched docs
ids = generate_id_choices(fetched_docs, query)

# identity which datasets were chosen
chosen_dataset_names = [dataset_docs_dict[id].name for id in ids]
print(f"Chosen datasets that match the query {query}: {chosen_dataset_names}")


# get the datasets from the ids
start = time.time()
chosen_dataset_full = loop.run_until_complete(
    aget_datasets_from_ids(ids)
)
print(
    f"Obtained {len(chosen_dataset_full)} datasets in {time.time() - start} seconds.")


if __name__ == "__main__":
    pass
