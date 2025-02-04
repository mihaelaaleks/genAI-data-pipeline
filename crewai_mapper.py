import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import AzureOpenAI
from pathlib import Path

# Parse .env and load all variables as environment variables
load_dotenv()

# Initialize an instance of AzureOpenAI for GPT-3.5
# This setup connects to Azure's OpenAI service using environment variables for secure configuration.
# Tutorial explanation from CrewAI docs: https://docs.crewai.com/how-to/Creating-a-Crew-and-kick-it-off/#step-1-assemble-your-agents
GPT35 = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_ENDPOINT"),
    openai_api_version="2023-07-01-preview",
    azure_deployment=os.environ.get("GPT_DEPLOYMENT_NAME"),
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    openai_api_type="azure",
    max_tokens= -1
)

# Define input and output directories of CrewAI with path objects 
INPUT_PATH = Path("./input_data")
OUTPUT_PATH = Path("./output_data")

data_analyst = Agent(
  role='Experienced Data Analyst',
  goal='Analyse accounting data from an input format and figure out which columns can be mapped to a set output format.',
  verbose=True,
  memory=True,
  backstory=(
  """You have over 10 years of experience as a data analyst and engineer.
  You are able to look at an input dataset and a list of output columns and see which input dataset 
  columns correspond to what output column names. You respond only with the useful information and in English.
  """
  ),
  tools=[],
  allow_delegation=True,
  llm=GPT35
)

analyse_output = Task(
  description=(
  """
  Given a set of columns: {expected}. Match the items from the set to a column from this dataset: {dataset}.
  Give a concise answer only with the potential matches, do not give explanations. 
  """
  ),
  expected_output="Return only the potential matches to the {expected} columns in this format: {format}",
  tools=[],
  agent=data_analyst,
  async_execution=False,
  output_file = str(OUTPUT_PATH / 'outputReport.md')
)

mapping_crew = Crew(
  agents=[data_analyst], 
  tasks=[analyse_output], 
  process=Process.sequential
)

# This expected format seems to work on first try. 
# TO-DO: Explore different ways to receive more structured responses. 
format = "-->expected_column -->dataset_column"

    
def get_mapping(expected: list, input: str):
    result = mapping_crew.kickoff(inputs={'dataset': input, 'expected': expected, 'format': format})
    return result