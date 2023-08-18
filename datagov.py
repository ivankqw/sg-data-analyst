from typing import List, Dict, Any
import requests
import aiohttp
import asyncio
from definitions.dataset import Dataset
from requests import JSONDecodeError
from ast import literal_eval

# Define the URLs - API v1
package_list_url: str = "https://data.gov.sg/api/action/package_list"
package_show_url: str = "https://data.gov.sg/api/action/package_show?id="
dataset_search_url = "https://data.gov.sg/api/action/datastore_search?resource_id="


def get_dataset_names(package_list_url: str = package_list_url) -> List[str]:
    """Returns a list of dataset names.

    :param package_list_url: the url to get the list of datasets :class `str`

    :return: a list of dataset names :class `List[str]`
    """
    res = requests.get(package_list_url)
    result = res.json()['result']
    return result


def get_dataset_metadata(dataset_name: str, package_show_url: str = package_show_url) -> dict:
    """Returns the metadata of a dataset.

    :param dataset_name: the name of the dataset :class `str`
    :param package_show_url: the url to get the metadata of a dataset :class `str`

    :return: the metadata of a dataset :class `dict`
    """
    res = requests.get(f"{package_show_url}{dataset_name}")
    result = res.json()['result']
    return result


async def aget_dataset_metadata(session: aiohttp.ClientSession, dataset_name: str, package_show_url: str = package_show_url) -> dict:
    """Returns the metadata of a dataset. This is done asynchronously.

    :param session: the aiohttp session :class `aiohttp.ClientSession`
    :param dataset_name: the name of the dataset :class `str`
    :param package_show_url: the url to get the metadata of a dataset :class `str`

    :return: the metadata of a dataset :class `dict`
    """
    async with session.get(f"{package_show_url}{dataset_name}") as res:
        result = await res.json()
        return result['result']


def get_csv_datasets(package_list_url: str, package_show_url: str = package_show_url) -> List[Dataset]:
    """Returns the datasets that are in CSV format.

    :param package_list_url: the url to get the list of datasets :class `str`
    :param package_show_url: the url to get the metadata of a dataset :class `str`

    :return: a list of datasets that are in CSV format :class `List[Dataset]`
    """
    datasets = get_dataset_names(package_list_url)
    csv_datasets = []
    for dataset in datasets:
        metadata = get_dataset_metadata(dataset, package_show_url)
        resources = metadata['resources']
        for resource in resources:
            if resource['format'] == 'CSV':
                csv_datasets.append(Dataset(
                    id=resource['id'],
                    name=dataset,
                    description=metadata['description'],
                ))
    return csv_datasets


async def aget_csv_datasets(package_list_url: str = package_list_url, package_show_url: str = package_show_url) -> List[Dataset]:
    """Returns the datasets that are in CSV format. This is done asynchronously.

    :param package_list_url: the url to get the list of datasets :class `str`
    :param package_show_url: the url to get the metadata of a dataset :class `str`

    :return: a list of datasets that are in CSV format :class `List[Dataset]`
    """
    datasets = get_dataset_names(package_list_url)
    csv_datasets = []
    tasks = []
    async with aiohttp.ClientSession() as session:
        for dataset in datasets:
            task = asyncio.ensure_future(aget_dataset_metadata(
                session, dataset, package_show_url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

        for i, response in enumerate(responses):
            resources = response['resources']
            for resource in resources:
                if resource['format'] == 'CSV':
                    csv_datasets.append(Dataset(
                        id=resource['id'],
                        name=datasets[i],
                        description=response['description'],
                    ))
    return csv_datasets

def _parse_results(result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parses the results from the dataset search.

    :param result: the result from the dataset search :class `List[Dict[str, Any]]`

    :return: the parsed result :class `List[Dict[str, Any]]`
    """
    # TODO: 
    pass 

def get_dataset_from_id(id: str, dataset_search_url: str = dataset_search_url) -> Any:
    """Returns the dataset from the id.

    :param id: the id of the dataset :class `str`
    :param dataset_search_url: the url to get the dataset :class `str`

    :return: the dataset :class `Any`
    """
    url = dataset_search_url + id
    result = []
    while url:
        try:
            curr_json = requests.get(url).json()
            if not result:
                # first time
                result = curr_json["result"]["records"]
            elif curr_json["result"]["records"]:
                result.extend(curr_json["result"]["records"])
            else:  # no more records
                return result
            # check if there is a next page or prev and next not the same
            if ("next" in curr_json["result"]["_links"]) or (
                "prev" in curr_json["result"]["_links"]
                and curr_json["result"]["_links"]["next"]
                != curr_json["result"]["_links"]["prev"]
            ):
                url = dataset_search_url + curr_json["result"]["_links"]["next"]
            else:
                url = None
        # TODO: handle this better
        except Exception as e:
            print(e)
            return result  # return what we have so far
    return result


def get_datasets_from_ids(ids: List[str], dataset_search_url: str = dataset_search_url) -> Any:
    """Returns the dataset from the id.

    :param id: the id of the dataset :class `str`
    :param dataset_search_url: the url to get the dataset :class `str`

    :return: the dataset :class `Any`
    """

    datasets = []
    for id in ids:
        res = requests.get(f"{dataset_search_url}{id}")
        try:
            result = res.json()['result']
            next_url = result[0]['_links']['next']
            datasets.append(result)
        except JSONDecodeError:
            print(f"Could not retrieve dataset with id {id}.")
            continue

    return datasets


async def aget_datasets_from_ids(ids: List[str], dataset_search_url: str = dataset_search_url) -> Any:
    """Returns the dataset from the id. This is done asynchronously.

    :param id: the id of the dataset :class `str`
    :param dataset_search_url: the url to get the dataset :class `str`

    :return: the dataset :class `Any`
    """

    datasets = []
    tasks = []
    async with aiohttp.ClientSession() as session:
        for id in ids:
            task = asyncio.ensure_future(
                session.get(f"{dataset_search_url}{id}"))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

        for i, response in enumerate(responses):
            try:
                result = await response.json()
                datasets.append(result['result'])
            except JSONDecodeError:
                print(f"Could not retrieve dataset of id {ids[i]}.")
                continue

    return datasets
