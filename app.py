from openai_functions import generate_id_choices
from typing import List
from dotenv import load_dotenv, find_dotenv
import asyncio
from datagov import aget_csv_datasets, get_datasets_from_ids, _datasets_to_dataframes
from definitions.dataset import Dataset
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
import time
import termcolor
from pprint import pprint

_ = load_dotenv(find_dotenv())

color = "magenta"
query = "How was the weather generally like in February 2020?"

start = time.time()

loop = asyncio.get_event_loop()

csv_datasets: List[Dataset] = loop.run_until_complete(
    aget_csv_datasets()
)
# TODO: also a bottleneck, need to find a way to speed this up (8 seconds)
print(termcolor.colored(
    f"Obtained {len(csv_datasets)} datasets in {time.time() - start} seconds.", color))

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
print(termcolor.colored(
    f"loaded documents into vector store in {time.time() - start} seconds.", color))
fetched_docs = db.similarity_search(query)
print(termcolor.colored(f"found {len(fetched_docs)} candidate documents.", color))
pprint(termcolor.colored(f"top 5 documents that match the query {query}: {[x.page_content for x in fetched_docs[:5]]}", color))

# get the most relevant ids from the fetched docs
ids = generate_id_choices(fetched_docs, query)

# identify which datasets were chosen
chosen_dataset_names = [dataset_docs_dict[id].name for id in ids]
pprint(termcolor.colored(
    f"Chosen datasets that match the query {query}: {chosen_dataset_names}", color))

# get the datasets from the ids
start = time.time()
# TODO: potential bottleneck
chosen_dataset_full = get_datasets_from_ids(ids)
print(termcolor.colored(
    f"Obtained {len(chosen_dataset_full)} datasets in {time.time() - start} seconds."), color)

# convert to dataframes
chosen_dataset_dfs = _datasets_to_dataframes(chosen_dataset_full)
# print(f"Chosen datasets that match the query {query}: {chosen_dataset_dfs}")

llm = ChatOpenAI(temperature=0, model="gpt-4-0613")
agent = create_pandas_dataframe_agent(
    llm,
    chosen_dataset_dfs,
    verbose=True,
    AgentType=AgentType.OPENAI_FUNCTIONS,
)


if __name__ == "__main__":
    print(termcolor.colored(agent.run(query), color))
