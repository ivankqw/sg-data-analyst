from pprint import pprint
from typing import List, Tuple, Dict, Any
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
import asyncio
from datagov import aget_csv_datasets, get_datasets_from_ids
from definitions.dataset import Dataset
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS


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

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")


tools = [
    Tool(
        name="get_datasets_from_ids",
        func=get_datasets_from_ids,
        description="This is useful for when you need to retrieve datasets from a list of IDs.",
    )
]

agent = initialize_agent(
    tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)


prompt = f"""Given that you know the following datasets with information given in triple backticks:
```
{fetched_docs}
```

Retrieve the relevant datasets that can answer the following query given in triple backticks. If there are no relevant datasets, return an empty list.:
```
{query}
```
"""


if __name__ == "__main__":
    agent.run(prompt)
