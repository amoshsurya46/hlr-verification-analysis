import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
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

# Load data from JSON file or use sample data
try:
    if os.path.exists('hlr_data.json'):
        with open('hlr_data.json', 'r') as f:
            data = json.load(f)
    else:
        # Fallback sample data
        data = [
            {"operation": "SIMREG", "bss_msisdn": "60105211003", "hlr_msisdn": "HLR MSISDN NO DATA FOUND", "file_name": "hlrout_2025-07-13_10-45.txt"},
            {"operation": "CHANGEMSISDN", "bss_msisdn": "60192335883", "hlr_msisdn": "60105055478", "file_name": "hlrout_2025-07-13_08-45.txt"},
            {"operation": "SIMREG", "bss_msisdn": "60108010732", "hlr_msisdn": "HLR MSISDN NO DATA FOUND", "file_name": "hlrout_2025-07-13_12-00.txt"},
            {"operation": "CHANGEMSISDN", "bss_msisdn": "60176364408", "hlr_msisdn": "601135250267", "file_name": "hlrout_2025-07-13_08-45.txt"}
        ]
except:
    data = [{"operation": "SIMREG", "bss_msisdn": "60105211003", "hlr_msisdn": "HLR MSISDN NO DATA FOUND", "file_name": "sample.txt"}]

# Header
st.markdown('<h1 class="main-header">📊 HLR Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">🔧 Analysis Controls</div>', unsafe_allow_html=True)
    
    # Operation filter
    st.subheader("⚙️ Operation Filter")
    operation_filter = st.selectbox(
        "Select Operation",
        ["All", "SIMREG", "CHANGEMSISDN"]
    )
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary"):
        st.rerun()
    
    st.info("💡 This is a demo version with sample data. Local version has full functionality.")

# Filter data
df = pd.DataFrame(data)
if operation_filter != "All":
    df = df[df['operation'] == operation_filter]

if df.empty:
    st.warning("⚠️ No data found for selected criteria")
    st.stop()

# Key Metrics
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Records", f"{len(df):,}")

with col2:
    simreg_count = len(df[df['operation'] == 'SIMREG'])
    st.metric("📱 SIMREG", f"{simreg_count:,}")

with col3:
    change_count = len(df[df['operation'] == 'CHANGEMSISDN'])
    st.metric("🔄 CHANGEMSISDN", f"{change_count:,}")

with col4:
    success_rate = len(df[~df['hlr_msisdn'].str.contains('NO DATA FOUND', na=False)]) / len(df) * 100 if len(df) > 0 else 0
    st.metric("✅ Success Rate", f"{success_rate:.1f}%")

# Charts Section
st.subheader("📊 Analytics")

tab1, tab2, tab3 = st.tabs(["🥧 Distribution", "📋 Data Quality", "📁 Files"])

with tab1:
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

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Data quality metrics
        quality_metrics = {
            'Total Records': len(df),
            'Records with HLR Data': len(df[df['hlr_status'] == 'Data Found']),
            'Records without HLR Data': len(df[df['hlr_status'] == 'No Data Found']),
            'Unique MSISDN': df['bss_msisdn'].nunique(),
            'Unique Operations': df['operation'].nunique()
        }
        
        st.markdown("### 📋 Data Quality Summary")
        for metric, value in quality_metrics.items():
            st.metric(metric, f"{value:,}")
    
    with col2:
        # Success rate by operation
        success_by_op = df.groupby('operation').apply(
            lambda x: len(x[x['hlr_status'] == 'Data Found']) / len(x) * 100
        ).reset_index(name='success_rate')
        
        fig_success = px.bar(
            success_by_op, x='operation', y='success_rate',
            title="📈 Success Rate by Operation (%)",
            color_discrete_sequence=['#667eea']
        )
        fig_success.update_yaxes(title="Success Rate (%)")
        st.plotly_chart(fig_success, use_container_width=True)

with tab3:
    if 'file_name' in df.columns:
        # File distribution
        file_data = df.groupby('file_name').size().reset_index(name='count').sort_values('count', ascending=False)
        fig_files = px.bar(
            file_data.head(10), x='count', y='file_name',
            title="📁 Top 10 Files by Record Count",
            orientation='h',
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig_files, use_container_width=True)
    else:
        st.info("File information not available in current dataset")

# Recent Records
st.subheader("🕒 Recent Records")
if 'file_name' in df.columns:
    display_df = df[['operation', 'bss_msisdn', 'hlr_msisdn', 'file_name']].head(20)
else:
    display_df = df[['operation', 'bss_msisdn', 'hlr_msisdn']].head(20)
st.dataframe(display_df, use_container_width=True)

# Export functionality
st.subheader("💾 Export Data")
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Download Data (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"hlr_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col2:
    st.info(f"📊 Showing {len(df):,} records | Filter: {operation_filter}")