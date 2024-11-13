import pandas as pd
from sqlalchemy import create_engine, text

import streamlit as st

class SnowflakeDatabase:

    def __init__(self) -> None:
        self.engine = self.initialize_engine()
        self.connection = self.engine.connect()

    def initialize_engine(self):

        try:
            engine = create_engine(
            'snowflake://{user}:{password}@{account_identifier}/{database_name}/{schema_name}'.format(
                user=st.secrets["SNOWFLAKE_USER"],
                password=st.secrets["SNOWFLAKE_PASSWORD"],
                account_identifier=st.secrets["SNOWFLAKE_ACCOUNT_IDENTIFIER"],
                database_name=st.secrets["SNOWFLAKE_DATABASE_NAME"],
                schema_name=st.secrets["SNOWFLAKE_SCHEMA_NAME"]
            )
            )

            return engine
        except Exception as e:
            raise Exception(f"Unable to initalize snowflake database : {e}")


    def get_dataframe_from_snowflake(self , sql)->pd.DataFrame:

        try :

            df = pd.read_sql_query(text(sql), self.connection)
            return df
        
        except Exception as e:

            raise Exception(f"Error Occured while sending sql query to snowflake : \n SQL : {sql} \n\n {e}")



    def get_table_descriptions(self):

        try:
        
            tables_query = 'SHOW TABLES IN SCHEMA PUBLIC'
            tables_df = pd.read_sql_query(text(tables_query), self.connection)

            prompt = "Below is the schema information of various tables in the database, including table names and column details.\n\n"

            # Loop through each table and format the description
            for table_name in tables_df['name']:  # Adjust column name if needed
                desc_query = f"DESC TABLE {table_name}"
                desc_df = pd.read_sql_query(text(desc_query), self.connection)
                
                # Build the description for each table
                table_description = f"Table: {table_name}\nColumns:\n"
                for _, row in desc_df.iterrows():
                    column_name = row['name']           # Adjust column name if needed
                    column_type = row['type']           # Adjust type name if needed
                    table_description += f" - {column_name}: {column_type}\n"
                
                # Append each table's description to the prompt
                prompt += f"{table_description}\n"

            # Display the prompt with formatted table descriptions
            print(prompt)
            return prompt
        except Exception as e:

            raise Exception(f"Error Occured while raising getting sql queries froms snowflake : {e}")