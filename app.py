from pprint import pprint
from typing import List, Tuple, Dict
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import asyncio
from datagov import get_dataset_names, aget_csv_datasets


# load environment variables by finding the .env file
load_dotenv()

# Define the URLs - API v1
package_list_url: str = "https://data.gov.sg/api/action/package_list"
package_show_url: str = "https://data.gov.sg/api/action/package_show?id="

loop = asyncio.get_event_loop()
# list of dictionaries containing dataset ids, names, descriptions
# TODO: create a dataclass for this instead of using a dictionary
csv_datasets: List[Dict[str, str]] = loop.run_until_complete(
    aget_csv_datasets(package_list_url, package_show_url)
)

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")


if __name__ == "__main__":
    print("hello world")
    print(csv_datasets)
