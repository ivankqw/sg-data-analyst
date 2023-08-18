from ast import literal_eval
from typing import List, Dict, Any
import openai
from prompts import get_dataset_ids_prompt
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import GPT_MODEL


def chat_with_retry(**kwargs) -> Any:
    @retry(
        wait=wait_exponential(min=4, max=10),
        stop=stop_after_attempt(10),
        retry=(
            retry_if_exception_type(openai.error.RateLimitError)
            | retry_if_exception_type(openai.error.Timeout)
            | retry_if_exception_type(openai.error.APIError)
            | retry_if_exception_type(openai.error.APIConnectionError)
            | retry_if_exception_type(openai.error.RateLimitError)
            | retry_if_exception_type(openai.error.ServiceUnavailableError)
        ),
    )
    def _chat_with_retry(**kwargs: Any) -> Any:
        return openai.ChatCompletion.create(**kwargs)
    return _chat_with_retry(**kwargs)


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
    # get best ids using openai once, forcefully
    response = chat_with_retry(
        model=GPT_MODEL,
        messages=messages,
        functions=functions,
        function_call={"name": "get_datasets_from_ids"},
        temperature=0,
    )

    try:
        ids_raw = response["choices"][0]["message"]["function_call"]["arguments"]
        # then parse the arguments
        ids_dict = literal_eval(ids_raw)
        ids = ids_dict["ids"]
    except KeyError:
        print("Could not retrieve ids.")
        ids = []

    return ids
