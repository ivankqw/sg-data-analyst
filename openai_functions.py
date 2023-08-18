from ast import literal_eval
from typing import List, Dict
import openai
from prompts import get_dataset_ids_prompt

GPT_MODEL: str = "gpt-3.5-turbo-16k-0613"


def generate_id_choices(fetched_docs: List[Dict[str, str]], query: str) -> List[str]:
    """Generates the choices for the ids of the datasets.

    :param fetched_docs: the fetched documents :class `List[Dict[str, str]]`
    :param query: the query :class `str`

    :return: the ids of the datasets :class `List[str]`
    """

    messages: List[Dict[str, str]] = [
        {"role": "user", "content": get_dataset_ids_prompt(fetched_docs, query)}]

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
        print("there was an error with openai, skipping.")
        response = {}

    try:
        ids_raw = response["choices"][0]["message"]["function_call"]["arguments"]
        # then parse the arguments
        ids_dict = literal_eval(ids_raw)
        ids = ids_dict["ids"]
    except KeyError:
        print("Could not retrieve ids.")
        ids = []

    return ids
