import streamlit as st
from dataclasses import dataclass
from dataBot import DataBot
from uuid import uuid4
import pandas as pd
from random import randint
import altair as alt
import time
_LOREM_IPSUM = """
Chat History is not avaliable.
"""
def stream_data():
    for word in _LOREM_IPSUM.split(" "):
        yield word + " "
        time.sleep(0.02)

if "thread" not in st.session_state:
    st.session_state["thread"] = []

if "DataBot" not in st.session_state:
    st.session_state["DataBot"] = DataBot()


st.set_page_config(layout="wide")

col1 ,col2 = st.columns([1,1])

with col1:
    for message in st.session_state["thread"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if question := st.chat_input("What how many constomer comlplaints have I been getting every year?"):

    with col1:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            # response = st.session_state["DataBot"].respond(question)
            # st.write(st.session_state["DataBot"].respond(question))
            # response = st.session_state["DataBot"].respond(question)
            # print(response)
            # for res in response:
            #     st.code(res["sql"] , language="sql")
            for response in st.session_state["DataBot"].respond(question):
                with st.container(border=True):
                    # for chunk in st.session_state["DataBot"].get_graph_heading(response["sql"] , response["dataframe"]):
                    #     st.write(chunk)
                    st.write_stream(st.session_state["DataBot"].get_graph_heading(response["sql"] , response["dataframe"]))
                    # st.code(response["sql"] , language="sql")
                    st.altair_chart(response["chart"] , use_container_width=True)
                    st.write_stream(st.session_state["DataBot"].get_recommendations(response["sql"] , response["dataframe"]))
                
            


    st.session_state["thread"].append({"role" : "user" , "content" : question})
    st.session_state["thread"].append({"role" : "assistant" , "content" : _LOREM_IPSUM})

# Right-half section of the screen
with col2:
    st.header("Today's Summary")

    # Snapshot Scores Section
    st.subheader("Snapshot Scores")

    sc1, sc2 = st.columns([1, 1])
    with sc1:
        # Display snapshot for Customer Complaints
        st.metric(label="Customer Complaints", value="Good", delta="-15% from last month")
        st.write("Complaints have improved this month, reflecting better control.")

    with sc2:
        # Display snapshot for PackerQA status
        st.metric(label="PackerQA", value="Under Control", delta="+10% improvement from last month")
        st.write("PackerQA is expected to be in control this month after recent interventions.")

    # Forecast Graph Section
    st.subheader("Forecasted Trends")

    # Generate and display mock data for forecasted trends
    forecast_data = pd.DataFrame({
        'Month': ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan'],
        'Customer Complaints': [randint(90, 120), randint(110, 140), randint(80, 110), randint(60, 90), randint(50, 70), randint(40, 60)],
        'PackerQA': [randint(40, 80), randint(30, 70), randint(20, 50), randint(10, 40), randint(5, 35), randint(0, 30)]
    })

    # Mark only the last point as forecasted
    forecast_data['Forecast'] = ['Actual'] * 5 + ['Forecast']

    # Altair line chart with forecasted point in different color and shape
    base_chart = alt.Chart(forecast_data).transform_fold(
        ['Customer Complaints', 'PackerQA'],
        as_=['Category', 'Value']
    )

    # Line for actual data points
    line_chart = base_chart.mark_line().encode(
        x='Month',
        y=alt.Y('Value:Q', title='Score'),
        color='Category:N'
    )

    # Highlight only the last point as forecasted with different color and shape
    points_chart = base_chart.mark_point().encode(
        x='Month',
        y='Value:Q',
        color=alt.condition(
            alt.datum.Forecast == 'Forecast',
            alt.value('orange'),  # Color for forecasted point
            alt.Color('Category:N')  # Default color for actual points
        ),
        shape=alt.condition(
            alt.datum.Forecast == 'Forecast',
            alt.value('diamond'),   # Shape for forecasted point
            alt.value('circle')     # Shape for actual points
        ),
        tooltip=['Month', 'Category:N', 'Value:Q']
    )

    # Combine line and points charts
    combined_chart = (line_chart + points_chart).properties(
        width=500,
        title="Projected Scores for Customer Complaints and PackerQA"
    )

    st.altair_chart(combined_chart, use_container_width=True)

    # Actionable Insights Section
    st.subheader("Recommended Actions")

    # Recommended actions for each metric in two columns within the right column
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Customer Complaints")
        st.write("- Continue monitoring key complaint drivers.")
        st.write("- Introduce proactive measures for common issues.")
        st.button("View Detailed Analysis", key="customer_complaints_button")

    with col2:
        st.markdown("### PackerQA")
        st.write("- Maintain newly implemented controls.")
        st.write("- Schedule quality audits for early next month.")
        st.button("View Detailed Analysis", key="packerqa_button")