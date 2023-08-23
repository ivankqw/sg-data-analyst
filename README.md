# sg-data-analyst

[Medium Article](https://ivankqw.medium.com/sg-data-analyst-question-answering-over-a-dataset-repository-with-reasoning-agents-dab7f05ed8bf)

## Explore Singapore Datasets with SG Data Analyst 🤖

Based on your query, SG Data Analyst will find the most relevant datasets from [data.gov.sg](https://data.gov.sg/) and [data.gov.sg's API](https://developers.data.gov.sg/). 

Using Langchain's Pandas DataFrame Agent, SG Data Analyst will then perform exploratory data analysis on the datasets and gather insights to answer your query.

## Quickstart

1. Install requirements
```
pip install -r requirements.txt
```
2. Add your OpenAI API key to the environment

- It's best to have access to GPT-4, `gpt-4-0613` in particular since we rely on the [OpenAI functions API](https://openai.com/blog/function-calling-and-other-api-updates)
- Alternatively, `gpt-3.5-turbo-0613` or `gpt-3.5-turbo-16k-0613` should work as well, though not as well as GPT-4
- Changes can be made in `config.py` 
```
export OPENAI_API_KEY=<your-api-key>
```
Alternatively, you can add your API key to a `.env` file in the root directory of this project. Refer to `dev.env` for the format.

3. Run the streamlit app
```
streamlit run app.py
```
4. Try it out!

>😃: What are some observations in university education?

>👨‍🔬: Some observations in university education based on the data include:
>1. The data covers a wide range of fields of study, including 'Accountancy', 'Architecture, Building & Real Estate', 'Business & Administration', 'Dentistry', 'Education', 'Engineering Sciences', 'Fine & Applied Arts', 'Health Sciences', 'Humanities & Social Sciences', 'Information Technology', 'Law', 'Mass Communication', 'Medicine', 'Natural, Physical & Mathematical Sciences', 'Services', and 'Natural & Mathematical Sciences'.
>2. The data includes information on both male and female students, as well as a combined category for both sexes.
>3. The data covers a wide range of years, from 1982 to 2021.






