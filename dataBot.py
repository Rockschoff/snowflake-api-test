import time
import altair as alt
import pandas as pd
from openai import OpenAI
import streamlit as st
from typing import Optional

from tools.SQLGenerator import SQLGenerator
from tools.GraphGenerator import GraphGenerator
from tools.utils import get_function_output
class DataBot:

    def __init__(self):
        self.sql_generator = SQLGenerator()
        self.graph_generator = GraphGenerator()
        try:
            self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        except Exception as e:

            raise Exception(f"Error Occured while initializing openai : {e}")
        

    def respond(self, question):
        
        sql_n_charts = self.sql_generator.get_sql_n_charts(question)#[{"sql" , "chart_type"}]

        print(sql_n_charts)
        response = []
        for sql_n_chart in sql_n_charts:
            try:
                dataframe = self.sql_generator.get_dataframe_from_snowflake(sql_n_chart["sql"])
                chart = self.graph_generator.generate_graph(dataframe , sql_n_chart["chart_type"])
                ele = {
                    "sql" : sql_n_chart["sql"],
                    "dataframe" : dataframe,
                    "chart" : chart
                }
                response.append(ele)
                yield ele
                print(dataframe)
            except Exception as e:
                print(e)

    def get_graph_heading(self , sql : str , dataframe : pd.DataFrame):

        completion = self.client.chat.completions.create(

            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Give  the sql statement please give a succinct and precise heading for  the graph that this query will represent SQL : {sql}"}
            ],
            stream=True
        )

        for chunk in completion:
            yield chunk.choices[0].delta.content

    def get_recommendations(self , sql :str , dataframe : pd.DataFrame , chart: Optional[alt.Chart] = None):

        prompt = """You are given a sql statement and a snapshot of the dataset that is result of the query. please look that this data in the light of niagara documents and give 3-4 recommendations and actionable step regarding this. Please provide citations for these recommndations as well
        SQL Statement : {sql}
        Data : {data}
        
        Just give two sections, recommendations and citations
        each recommendation should be short and two the point. it should point the problem in one sentence and actinaable step the next sentence, 3-4 recommendations are enough
        Do not give recommendation if not immediate actions are needed """

        stream = self.client.beta.threads.create_and_run(
            thread={
                "messages" : [
                    {"role" : "user" , "content" : prompt.format(sql=sql , data=dataframe.head(50).to_markdown(index=False))}
                ]
            },
            assistant_id=st.secrets["OPENAI_ASSISTANT_ID"],
            stream=True,
            tool_choice={"type": "function", "function": {"name": "Search_Niagara_Documents"}}
        )
        tool_outputs=[]
        run_id=""
        thread_id=""
        for event in stream:
            if event.event=="thread.run.requires_action":
                run_id = event.data.id
                thread_id=event.data.thread_id
                for tool_call in event.data.required_action.submit_tool_outputs.tool_calls:
                    function_name = tool_call.function.name
                    function_arguments= tool_call.function.arguments
                    output = get_function_output(function_name , function_arguments)
                    tool_outputs.append({"tool_call_id" : tool_call.id , "output" : output})
                break

        if run_id and thread_id:
            stream = self.client.beta.threads.runs.submit_tool_outputs(
                run_id=run_id,
                thread_id=thread_id,
                tool_outputs=tool_outputs,
                stream=True
            )

            for event in stream:
                if event.event=="thread.message.delta" and isinstance(event.data.delta.content[0].text.value , str):

                    text = event.data.delta.content[0].text.value
                    yield text

        else:

            yield "Recommendations not available"

            



                

        

        


        # # First response
        # yield "this"
        # time.sleep(2)
        # yield f"This is a response to {question}"

        # # Generate a sample Altair chart as a JSON object
        # df = pd.DataFrame({
        #     'x': range(1, 6),
        #     'y': [1, 3, 2, 4, 5]
        # })
        
        # chart = alt.Chart(df).mark_line().encode(
        #     x='x:Q',
        #     y='y:Q'
        # ).properties(
        #     title=f"Demo Chart for: {question}"
        # )
        
        # # Yield chart JSON after a delay
        # time.sleep(1)
        # yield chart

        # # Additional response
        # time.sleep(1)
        # yield "Second bit"

