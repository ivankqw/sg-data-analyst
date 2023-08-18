from typing import List
from dotenv import load_dotenv, find_dotenv
import asyncio

from config import GPT_MODEL
from definitions.dataset import Dataset
from api.openai_functions import generate_id_choices
from api.datagov import aget_csv_datasets, get_datasets_from_ids, _datasets_to_dataframes
from vector_store import split_and_store, similarity_search

from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType

import time
import termcolor

_ = load_dotenv(find_dotenv())

source_url_base = "https://legacy.data.gov.sg/dataset/"
color = "magenta"


class SGDataAnalystAgent:
    @staticmethod
    def run(query: str) -> str:
        """Runs the agent on a query.

        :param query: the query :class `str`

        :return: the response :class `str`
        """
        start = time.time()
        csv_datasets: List[Dataset] = asyncio.run(aget_csv_datasets())

        # TODO: Bottleneck
        print(termcolor.colored(
            f"Obtained {len(csv_datasets)} datasets in {time.time() - start} seconds.", color))

        dataset_docs = [dataset.to_document() for dataset in csv_datasets]
        # put them into a dictionary as well for easy access
        dataset_docs_dict = {dataset.id: dataset for dataset in csv_datasets}

        # Load the document, split it into chunks, embed each chunk and load it into the vector store.
        db = split_and_store(dataset_docs)
        fetched_docs = similarity_search(db, query)

        # get the most relevant ids from the fetched docs
        ids = generate_id_choices(fetched_docs, query)

        # identify which datasets were chosen
        chosen_dataset_names = [dataset_docs_dict[id].name for id in ids]

        # get the datasets from the ids
        start = time.time()
        # TODO: Slight bottleneck
        chosen_datasets_full = get_datasets_from_ids(ids)
        print(termcolor.colored(
            f"Obtained {len(chosen_datasets_full)} datasets in {time.time() - start} seconds."), color)

        # convert to dataframes
        chosen_dataset_dfs = _datasets_to_dataframes(chosen_datasets_full)

        llm = ChatOpenAI(temperature=0, model=GPT_MODEL)
        agent = create_pandas_dataframe_agent(
            llm,
            chosen_dataset_dfs,
            verbose=True,
            AgentType=AgentType.OPENAI_FUNCTIONS,
        )
        print(termcolor.colored(
            f'Answering query "{query}" with the following datasets: {chosen_dataset_names}', "yellow"))
        return agent.run(query)
