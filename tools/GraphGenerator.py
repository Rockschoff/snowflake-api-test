import pandas as pd
import altair as alt
import re

class GraphGenerator:

    def __init__(self) -> None:
        pass

    def clean_column_name(self, column_name: str) -> str:
        # Strip unwanted characters that might cause Altair issues
        return re.sub(r'[^\w\s]', '', column_name).strip()

    def generate_graph(self, dataframe: pd.DataFrame, chart_type: str) -> alt.Chart:
        
        # Ensure there are enough columns in the data
        if len(dataframe.columns) < 2:
            x_column = dataframe.index.name or "index"  # Use index as x-axis if <2 columns
            dataframe = dataframe.reset_index()  # Reset index so it can be used as a column
            y_column = dataframe.columns[1] if len(dataframe.columns) > 1 else dataframe.columns[0]
        else:
            x_column, y_column = dataframe.columns[0], dataframe.columns[1]

        # Clean column names for compatibility with Altair
        x_column_cleaned = self.clean_column_name(x_column)
        y_column_cleaned = self.clean_column_name(y_column)

        # Rename columns in the dataframe for Altair compatibility
        dataframe = dataframe.rename(columns={x_column: x_column_cleaned, y_column: y_column_cleaned})

        if chart_type == "line_chart":
            return alt.Chart(dataframe).mark_line().encode(
                x=x_column_cleaned,
                y=y_column_cleaned
            )
        elif chart_type == "bar_chart":
            return alt.Chart(dataframe).mark_bar().encode(
                x=x_column_cleaned,
                y=y_column_cleaned
            )
        elif chart_type == "scatter_chart":
            return alt.Chart(dataframe).mark_circle().encode(
                x=x_column_cleaned,
                y=y_column_cleaned
            )
        else:
            empty_df = pd.DataFrame()
            return alt.Chart(empty_df).mark_point().encode()
