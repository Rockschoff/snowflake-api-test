import json
import tiktoken
encoder = tiktoken.get_encoding("cl100k_base")

import streamlit as st

from openai import OpenAI

from pydantic import BaseModel
from typing import List
from enum import Enum

class ChartType(str, Enum):
    line_chart = "line_chart"
    bar_chart = "bar_chart"
    scatter_chart = "scatter_chart"

class SQLQuery(BaseModel):
    sql: str
    chart_type: ChartType

class SQLQueryList(BaseModel):
    sql_query_list: List[SQLQuery]


GET_STRUCT_SQL_PROMPT_TEMPLATE = """
You are an intelligent Niagara SQL Data Analyst for the Food Safety and Quality department.
You can search for relevant applications by using the "Search_Niagara_Documents" tool to find specific terms.

Your job is to provide SQL queries and the appropriate chart types to visualize the data. Format your response as follows:
a list of items, each item in the format {{"sql": string, "chart_type": enum(["line_chart", "bar_chart", "scatter_chart"])}}, where each item represents one graph suggestion.

Guidelines:
1) If helpful, search for any useful information by looking up terms in "Search_Niagara_Documents".
2) Choose the relevant tables and columns from schemas available in the vector store documents.
3.1) Provide syntactically correct SQL queries for the question, where each query returns **exactly two columns** for compatibility with the graph, with the first column as the x-axis and the second as the y-axis.
   - Always use double quotes around table and column names to handle case sensitivity (e.g., `"AGR"`, `"Date"`, `"Sensor10"`).
   - If you can't determine the queries.
3.2) Specify the chart type for each query. Only use the following options: ["line_chart", "bar_chart", "scatter_chart"].

### Output Format Examples:

Example Output 1:
"{{"sql_query_list":[
    {{"sql": "SELECT "Date", "Sensor12" FROM "AGR";", "chart_type": "line_chart"}},
    {{"sql": "SELECT "Employee", AVG("Sensor10") FROM "AGR" GROUP BY "Employee";", "chart_type": "bar_chart"}}
]}}"

Example Output 2:
"{{"sql_query_list" : [
    {{"sql": "SELECT "InspectionDate", "QualityScore" FROM "QualityControl" WHERE "Location" = 'Plant A';", "chart_type": "scatter_chart"}},
    {{"sql": "SELECT "BatchID", "DefectCount" FROM "Production" WHERE "DefectCount" > 0;", "chart_type": "bar_chart"}}
]}}"

Example Output 3:
"{{"sql_query_list" : [
    {{"sql": "SELECT "Year", "TotalProduction" FROM "AnnualReport";", "chart_type": "line_chart"}},
    {{"sql": "SELECT "Month", SUM("DefectCount") FROM "QualityMetrics" GROUP BY "Month";", "chart_type": "bar_chart"}},
    {{"sql": "SELECT "Shift", AVG("Temperature") FROM "ProductionMetrics" GROUP BY "Shift";", "chart_type": "scatter_chart"}}
]}}"


ounly give the list of queries are nothing else, just are string that can be parsed as json

Ensure each query has only two columns and is formatted as a list. Here is the User Query: {query}

Description of all the tables in the database : {table_descriptions}
"""

class StructuredLLM:

    def __init__(self) -> None:
        try:
            self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        except Exception as e:

            raise Exception(f"Error Occured while initializing openai : {e}")

        

    def get_strcutired_sql_reponse(self , description , question):

        print("here")
        try:
            print("here as well")
            print(len(encoder.encode(GET_STRUCT_SQL_PROMPT_TEMPLATE.format(query=question , table_descriptions=description))))
            completion = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content":"return a sql query and the corresponding chart type"},
                    {"role": "user", "content": GET_STRUCT_SQL_PROMPT_TEMPLATE.format(query=question , table_descriptions=description)},
                ],
                response_format={ "type": "json_schema", "json_schema": {"name" : "sql_query_with_chart_name" , "schema" : SQLQueryList.model_json_schema()} },
            )

            event = completion.choices[0].message.content

            data = json.loads(event)

            data_list = data.get("sql_query_list" , "Error")

            if data_list != "Error":
                return data_list
            else:
                return []
        except Exception as err:

            raise f"Error Occured in structuredLLM , {err}"