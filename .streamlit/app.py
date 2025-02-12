import streamlit as st
import pandas as pd
import zipfile
import plotly.express as px
import plotly.graph_objects as go

# Function to read a CSV file from a ZIP archive
def read_zip_csv(zip_path, csv_filename):
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_filename) as f:
            return pd.read_csv(f)

# Paths to files (Modify these accordingly)
zip_path = "online+sales.zip"      # Replace with actual ZIP file path
csv_filename = "supermarket_sales.csv" # Name of CSV inside ZIP
csv_path = "file2.csv"     # Another CSV file outside ZIP

# Read data from ZIP and CSV files
df_zip = read_zip_csv(zip_path, csv_filename)
df_csv = pd.read_csv(csv_path)

# Merge/Concatenate Data (Modify as needed)
merged_df = pd.concat([df_zip, df_csv])

# Display Data
st.title("Customer Segmentation Dashboard")
st.dataframe(merged_df)

# Customer Segments Distribution
segment_counts = merged_df["segment"].value_counts()
fig_segments = px.pie(
    values=segment_counts.values,
    names=segment_counts.index,
    title="Customer Segments Distribution",
    color_discrete_sequence=px.colors.qualitative.Set3
)
st.plotly_chart(fig_segments)

# RFM Score Distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("RFM Score Distribution")
    fig_scores = go.Figure()
    for metric in ['r_score', 'f_score', 'm_score']:
        fig_scores.add_trace(go.Box(
            y=merged_df[metric],
            name=metric.upper(),
            boxpoints='outliers'
        ))
    st.plotly_chart(fig_scores)

with col2:
    st.subheader("Segment Characteristics")
    fig_chars = go.Figure(data=[
        go.Scatter3d(
            x=merged_df['recency'],
            y=merged_df['frequency'],
            z=merged_df['monetary'],
            mode='markers',
            marker=dict(
                size=5,
                color=merged_df['segment'].astype('category').cat.codes,
                colorscale='Viridis'
            )
        )
    ])
    st.plotly_chart(fig_chars)
