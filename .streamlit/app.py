import streamlit as st
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
y=segmented_df[metric],
name=metric.upper(),
boxpoints='outliers'
))
st.plotly_chart(fig_scores)

with col2:
st.subheader("Segment Characteristics")
fig_chars = go.Figure(data=[
go.Scatter3d(
x=segmented_df['recency'],
y=segmented_df['frequency'],
z=segmented_df['monetary'],
mode='markers',
marker=dict(
size=5,
color=segmented_df['segment'].astype('category').cat.codes,
colorscale='Viridis',
),
