#import libraries
import streamlit as st
import pandas as pd
import zipfile
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="RFM Analysis Dashboard", page_icon="📊", layout="wide")


# Function to read a CSV file from a ZIP archive
def read_zip_csv(zip_path, csv_filename):
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_filename) as f:
            return pd.read_csv(f)

# Paths to files 
zip_path = "online+sales.zip"      
csv_filename = "supermarket_sales.csv" 
csv_path = "file2.csv"    

# Read data from ZIP and CSV files
df_zip = read_zip_csv(zip_path, csv_filename)
df_csv = pd.read_csv(csv_path)

# Merge/Concatenate Data 
merged_df = pd.concat([df_zip, df_csv])

# Title/description
st.title("📊 RFM Analysis Dashboard")
st.markdown("""
This dashboard analyzes customer behavior using RFM (Recency, Frequency, Monetary) metrics:
* **Recency**: Days since last purchase
* **Frequency**: Number of purchases
* **Monetary**: Total spending
""")
# Sidebar filters for date and transaction amount
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Date'].min(), df['Date'].max()),
    min_value=df['Date'].min(),
    max_value=df['Date'].max(),
    key='date_range_filter'
)
transaction_amount = st.sidebar.slider(
    "Transaction Amount Range",
    min_value=float(df['Total'].min()),
    max_value=float(df['Total'].max()),
    value=(float(df['Total'].min()), float(df['Total'].max())),
    key='transaction_amount_slider'
)
# Filter data based on user input
filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) & 
    (df['Date'] <= pd.to_datetime(date_range[1])) &
    (df['Total'].between(transaction_amount[0], transaction_amount[1]))
]

# RFM Calculation
current_date = filtered_df['Date'].max()
rfm = filtered_df.groupby('Invoice ID').agg({
    'Date': lambda x: (current_date - x.max()).days,
    'Invoice ID': 'count',
    'Total': 'sum'
}).rename(columns={'Date': 'Recency', 'Invoice ID': 'Frequency', 'Total': 'Monetary'})

# Define bin edges for Recency, Frequency, and Monetary
recency_bins = [0, 30, 90, 180, 365]  # Example bins for Recency
frequency_bins = [1, 2, 5, 10, 20]    # Example bins for Frequency
monetary_bins = [0, 500, 1000, 5000, 10000]  # Example bins for Monetary

# Assign labels for the bins
recency_labels = ['1', '2', '3', '4']
frequency_labels = ['4', '3', '2', '1']
monetary_labels = ['4', '3', '2', '1']

# Segmenting with pd.cut
rfm['R'] = pd.cut(rfm['Recency'], bins=recency_bins, labels=recency_labels, include_lowest=True)
rfm['F'] = pd.cut(rfm['Frequency'], bins=frequency_bins, labels=frequency_labels, include_lowest=True)
rfm['M'] = pd.cut(rfm['Monetary'], bins=monetary_bins, labels=monetary_labels, include_lowest=True)

# Display RFM segments
st.dataframe(rfm)

# Calculate and display metrics
total_customers = rfm.shape[0]
average_recency = rfm['Recency'].mean()
average_frequency = rfm['Frequency'].mean()
average_monetary = rfm['Monetary'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", total_customers)
col2.metric("Average Recency", f"{average_recency:.2f} days")
col3.metric("Average Frequency", f"{average_frequency:.2f} purchases")
col4.metric("Average Monetary", f"${average_monetary:.2f}")

# Visualizations
fig_pie = px.pie(rfm, names='R', title='Customer Segments Distribution')
st.plotly_chart(fig_pie)

fig_box = go.Figure()
fig_box.add_trace(go.Box(y=rfm['Recency'], name="Recency"))
fig_box.add_trace(go.Box(y=rfm['Frequency'], name="Frequency"))
fig_box.add_trace(go.Box(y=rfm['Monetary'], name="Monetary"))
st.plotly_chart(fig_box)

fig_3d = px.scatter_3d(rfm, x='Recency', y='Frequency', z='Monetary', color='M')
st.plotly_chart(fig_3d)

# Export CSV feature
st.download_button(
    "Download RFM Data",
    rfm.to_csv(index=False).encode('utf-8'),
    "rfm_data.csv",
    "text/csv",
    key='download_csv_button'
)















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
