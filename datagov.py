from typing import List, Dict
import requests
import aiohttp
import asyncio


def get_dataset_names(package_list_url: str) -> List[str]:
    res = requests.get(package_list_url)
    result = res.json()['result']
    return result


async def aget_dataset_metadata(dataset_name: str, package_show_url: str, session: aiohttp.ClientSession) -> dict:
    """Returns the metadata of a dataset. This is done asynchronously.

    :param dataset_name: the name of the dataset :class `str`
    :param package_show_url: the url to get the metadata of a dataset :class `str`

    :return: the metadata of a dataset :class `dict`
    """
    async with session.get(f"{package_show_url}{dataset_name}") as res:
        result = await res.json()
        return result['result']


async def aget_csv_datasets(package_list_url: str, package_show_url: str) -> List[Dict[str, str]]:
    """Returns a list of dictionaries containing the dataset id, name and description of datasets that are in CSV format. This is done asynchronously.

    :param package_list_url: the url to get the list of datasets :class `str`
    :param package_show_url: the url to get the metadata of a dataset :class `str`

    :return: a list of dictionaries containing the dataset id, name and description of datasets that are in CSV format :class `List[Dict[str, str]]`
    """
    datasets = get_dataset_names(package_list_url)
    csv_datasets = []
    tasks = []
    async with aiohttp.ClientSession() as session:
        for dataset in datasets:
            task = asyncio.ensure_future(aget_dataset_metadata(
                dataset, package_show_url, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

        for i, response in enumerate(responses):
            resources = response['resources']
            for resource in resources:
                if resource['format'] == 'CSV':
                    csv_datasets.append({
                        'id': resource['id'],
                        'name': datasets[i],
                        'description': response['description'],
                    })
    return csv_datasets
