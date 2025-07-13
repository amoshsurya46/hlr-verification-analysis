import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="HLR Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
}
.sidebar-header {
    font-size: 1.5rem;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

def get_data(start_date=None, end_date=None, operation_filter=None):
    conn = mysql.connector.connect(
        host='mysql',
        user='hlruser',
        password='hlrpass',
        database='HLRDB'
    )
    
    query = "SELECT * FROM hlr_verification WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND DATE(record_timestamp) >= %s"
        params.append(start_date)
    if end_date:
        query += " AND DATE(record_timestamp) <= %s"
        params.append(end_date)
    if operation_filter and operation_filter != 'All':
        query += " AND operation = %s"
        params.append(operation_filter)
    
    query += " ORDER BY record_timestamp DESC"
    
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Header
st.markdown('<h1 class="main-header">📊 HLR Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">🔧 Analysis Controls</div>', unsafe_allow_html=True)
    
    # Date range selector
    st.subheader("📅 Date Range")
    date_option = st.selectbox(
        "Select Period",
        ["Last 7 Days", "Last 30 Days", "This Month", "Custom Range", "All Time"]
    )
    
    start_date, end_date = None, None
    if date_option == "Last 7 Days":
        start_date = (datetime.now() - timedelta(days=7)).date()
        end_date = datetime.now().date()
    elif date_option == "Last 30 Days":
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()
    elif date_option == "This Month":
        start_date = datetime.now().replace(day=1).date()
        end_date = datetime.now().date()
    elif date_option == "Custom Range":
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
    
    # Operation filter
    st.subheader("⚙️ Operation Filter")
    operation_filter = st.selectbox(
        "Select Operation",
        ["All", "SIMREG", "CHANGEMSISDN"]
    )
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary"):
        st.rerun()

# Load data
df = get_data(start_date, end_date, operation_filter)

if df.empty:
    st.warning("⚠️ No data found for selected criteria")
    st.stop()

# Convert timestamp
df['record_timestamp'] = pd.to_datetime(df['record_timestamp'])
df['date'] = df['record_timestamp'].dt.date
df['hour'] = df['record_timestamp'].dt.hour

# Key Metrics
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📊 Total Records",
        f"{len(df):,}",
        delta=f"+{len(df[df['date'] == datetime.now().date()]):,} today"
    )

with col2:
    simreg_count = len(df[df['operation'] == 'SIMREG'])
    st.metric("📱 SIMREG", f"{simreg_count:,}")

with col3:
    change_count = len(df[df['operation'] == 'CHANGEMSISDN'])
    st.metric("🔄 CHANGEMSISDN", f"{change_count:,}")

with col4:
    success_rate = len(df[~df['hlr_msisdn'].str.contains('NO DATA FOUND', na=False)]) / len(df) * 100
    st.metric("✅ Success Rate", f"{success_rate:.1f}%")

# Charts Section
st.subheader("📊 Analytics")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🥧 Distribution", "⏰ Hourly Pattern", "📋 Data Quality"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily trend
        daily_data = df.groupby('date').size().reset_index(name='count')
        fig_trend = px.line(
            daily_data, x='date', y='count',
            title="📈 Daily Transaction Trend",
            color_discrete_sequence=['#667eea']
        )
        fig_trend.update_layout(showlegend=False)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Operation trend
        op_daily = df.groupby(['date', 'operation']).size().reset_index(name='count')
        fig_op_trend = px.line(
            op_daily, x='date', y='count', color='operation',
            title="🔄 Operations Trend",
            color_discrete_sequence=['#667eea', '#764ba2']
        )
        st.plotly_chart(fig_op_trend, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Operation distribution
        fig_pie = px.pie(
            df, names='operation',
            title="⚙️ Operation Distribution",
            color_discrete_sequence=['#667eea', '#764ba2']
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # HLR data availability
        df['hlr_status'] = df['hlr_msisdn'].apply(
            lambda x: 'Data Found' if 'NO DATA FOUND' not in str(x) else 'No Data Found'
        )
        fig_status = px.bar(
            df.groupby(['operation', 'hlr_status']).size().reset_index(name='count'),
            x='operation', y='count', color='hlr_status',
            title="📊 HLR Data Availability by Operation",
            color_discrete_sequence=['#28a745', '#dc3545']
        )
        st.plotly_chart(fig_status, use_container_width=True)

with tab3:
    # Hourly pattern
    hourly_data = df.groupby('hour').size().reset_index(name='count')
    fig_hourly = px.bar(
        hourly_data, x='hour', y='count',
        title="⏰ Hourly Transaction Pattern",
        color_discrete_sequence=['#667eea']
    )
    fig_hourly.update_xaxes(title="Hour of Day")
    fig_hourly.update_yaxes(title="Transaction Count")
    st.plotly_chart(fig_hourly, use_container_width=True)

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        # File distribution
        file_data = df.groupby('file_name').size().reset_index(name='count').sort_values('count', ascending=False)
        fig_files = px.bar(
            file_data.head(10), x='count', y='file_name',
            title="📁 Top 10 Files by Record Count",
            orientation='h',
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig_files, use_container_width=True)
    
    with col2:
        # Data quality metrics
        quality_metrics = {
            'Total Records': len(df),
            'Records with HLR Data': len(df[df['hlr_status'] == 'Data Found']),
            'Records without HLR Data': len(df[df['hlr_status'] == 'No Data Found']),
            'Unique BSS MSISDN': df['bss_msisdn'].nunique(),
            'Unique BSS IMSI': df['bss_imsi'].nunique(),
            'Unique HLR MSISDN': df[df['hlr_status'] == 'Data Found']['hlr_msisdn'].nunique() if len(df[df['hlr_status'] == 'Data Found']) > 0 else 0
        }
        
        st.markdown("### 📋 Data Quality Summary")
        for metric, value in quality_metrics.items():
            st.metric(metric, f"{value:,}")

# Recent Records
st.subheader("🕒 Recent Records")
recent_df = df.sort_values('file_name', ascending=False).head(20)[['record_timestamp', 'operation', 'bss_msisdn', 'bss_imsi', 'hlr_msisdn', 'hlr_imsi', 'file_name']]
st.dataframe(recent_df, use_container_width=True)

# Export functionality
st.subheader("💾 Export Data")
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Download Filtered Data (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"hlr_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col2:
    st.info(f"📊 Showing {len(df):,} records from {df['date'].min()} to {df['date'].max()}")