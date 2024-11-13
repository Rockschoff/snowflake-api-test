from tools.SnowflakeDatabase import SnowflakeDatabase
from tools.StructuredLLM import StructuredLLM

import json

class SQLGenerator:
    def __init__(self) -> None:
        self.snowflake_database = SnowflakeDatabase()
        self.structured_llm = StructuredLLM()

    def get_sql_n_charts(self , question):
        

        table_descriptions = self.snowflake_database.get_table_descriptions()

        llm_response =  self.structured_llm.get_strcutired_sql_reponse(description=table_descriptions , question=question)
        
        return llm_response
    
    def get_dataframe_from_snowflake(self ,  sql):
        
        return self.snowflake_database.get_dataframe_from_snowflake(sql)

        
        
        

        