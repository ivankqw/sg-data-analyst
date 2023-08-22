def get_dataset_ids_prompt(fetched_docs, query):
    return f"""Given that you know the following datasets with information given in triple backticks:
```
{fetched_docs}
```

Retrieve the relevant datasets that can answer the following query given in triple backticks. If there are no relevant datasets, return an empty list.:
```
{query}
```
"""
    