import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Sample data for demo (replace with your actual data)
sample_data = [
    {"operation": "SIMREG", "bss_msisdn": "60105211003", "hlr_msisdn": "HLR MSISDN NO DATA FOUND"},
    {"operation": "CHANGEMSISDN", "bss_msisdn": "60192335883", "hlr_msisdn": "60105055478"},
    {"operation": "SIMREG", "bss_msisdn": "60108010732", "hlr_msisdn": "HLR MSISDN NO DATA FOUND"},
    {"operation": "CHANGEMSISDN", "bss_msisdn": "60176364408", "hlr_msisdn": "601135250267"}
]

st.title("HLR Verification Analysis")

df = pd.DataFrame(sample_data)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Records", len(df))
with col2:
    st.metric("SIMREG Operations", len(df[df['operation'] == 'SIMREG']))
with col3:
    st.metric("CHANGEMSISDN Operations", len(df[df['operation'] == 'CHANGEMSISDN']))

st.subheader("Operations Distribution")
fig = px.pie(df, names='operation', title="Operation Types")
st.plotly_chart(fig)

st.subheader("HLR Data Found vs Not Found")
df['hlr_data_found'] = df['hlr_msisdn'].apply(lambda x: 'Found' if 'NO DATA FOUND' not in x else 'Not Found')
fig2 = px.bar(df.groupby(['operation', 'hlr_data_found']).size().reset_index(name='count'), 
              x='operation', y='count', color='hlr_data_found', title="HLR Data Availability")
st.plotly_chart(fig2)

st.subheader("Sample Records")
st.dataframe(df)