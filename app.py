import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

def get_data():
    conn = mysql.connector.connect(
        host='mysql',
        user='hlruser',
        password='hlrpass',
        database='HLRDB'
    )
    df = pd.read_sql("SELECT * FROM hlr_verification", conn)
    conn.close()
    return df

st.title("HLR Verification Analysis")

df = get_data()

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

st.subheader("Recent Records")
st.dataframe(df.sort_values('record_timestamp', ascending=False).head(10))

st.subheader("All Records")
st.dataframe(df)