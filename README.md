# sg-data-analyst

## Explore Singapore Datasets with SG Data Analyst 🤖

Based on your query, SG Data Analyst will find the most relevant datasets from [data.gov.sg](https://data.gov.sg/) and [data.gov.sg's API](https://developers.data.gov.sg/). 

Using Langchain's Pandas DataFrame Agent, SG Data Analyst will then perform exploratory data analysis on the datasets and gather insights to answer your query.

## Quickstart

1. Install requirements
```
pip install -r requirements.txt
```
2. Add your OpenAI API key to the environment
```
export OPENAI_API_KEY=<your-api-key>
```
Alternatively, you can add your API key to a `.env` file in the root directory of this project. Please refer to `dev.env` for the format.

3. Run the streamlit app
```
streamlit run app.py
```




