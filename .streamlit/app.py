# Import necessary libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import pickle
import os
import hashlib
from datetime import datetime

# Set page config at the very beginning
st.set_page_config(page_title="RFM Analysis Dashboard", page_icon="📊", layout="wide")

# No database engine needed, we'll work with files directly

# Function to display the logo
def display_logo():
    # Use Streamlit's columns to position the logo
    cols = st.columns([1, 3])
    with cols[0]:
        # Display a placeholder image using st.image with a URL or local path
        # You can replace this URL with your own logo image path
        st.image("/Users/desiree/Desktop/Screen Shot 2025-03-03 at 7.44.49 PM.png", width=150)

# Create a file to store user credentials if it doesn't exist
def initialize_users():
    if not os.path.exists("users.pkl"):
        with open("users.pkl", "wb") as f:
            pickle.dump({}, f)

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to save users
def save_users(users):
    with open("users.pkl", "wb") as f:
        pickle.dump(users, f)

# Function to load users
def load_users():
    try:
        with open("users.pkl", "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return {}

# Function to register a new user
def register_user(username, password, email):
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists. Please choose another."
    
    # Create new user entry
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None
    }
    
    save_users(users)
    return True, "Registration successful! You can now login."

# Function to authenticate user
def authenticate(username, password):
    users = load_users()
    
    if username not in users:
        return False, "Username not found."
    
    stored_password = users[username]["password"]
    if stored_password == hash_password(password):
        # Update last login time
        users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        return True, "Login successful!"
    else:
        return False, "Incorrect password."

# Load your data
@st.cache_data  # Updated from st.cache
def load_data():
    # Replace with your file path
    df = pd.read_csv('supermarket_sales.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Authentication pages
def auth_page():
    # Display logo at the top of the auth page
    st.image("/Users/desiree/Desktop/Screen Shot 2025-03-03 at 7.44.49 PM.png", width=200)
    
    st.title("RFM Analysis Dashboard")
    
    # Add custom CSS
    st.markdown("""
    <style>
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .auth-header {
        text-align: center;
        color: #1E88E5;
        margin-bottom: 20px;
    }
    .tab-content {
        padding: 20px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.markdown("<h2 class='auth-header'>Login</h2>", unsafe_allow_html=True)
        
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.button("Login")
        
        if login_button:
            if not login_username or not login_password:
                st.error("Please enter both username and password")
            else:
                success, message = authenticate(login_username, login_password)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = login_username
                    st.success(message)
                    # Use rerun
                    st.rerun()
                else:
                    st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.markdown("<h2 class='auth-header'>Register</h2>", unsafe_allow_html=True)
        
        reg_user = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            register_button = st.button("Register")
        
        if register_button:
            if not reg_user or not reg_email or not reg_pass:
                st.error("Please fill in all fields")
            elif reg_pass != reg_confirm_pass:
                st.error("Passwords do not match")
            elif len(reg_pass) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                success, message = register_user(reg_user, reg_pass, reg_email)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main application function
def main():
    # Display logo in the top left corner of the main page
    display_logo()
    
    # Add logout button to sidebar
    if st.session_state.get("authenticated", False):
        st.sidebar.title(f"Welcome, {st.session_state['username']}!")
        if st.sidebar.button("Logout"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            # Use rerun
            st.rerun()
    
    # Add upload file functionality
    uploaded_file = st.sidebar.file_uploader("Upload your customer data CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            # Save the uploaded file locally (optional)
            # with open('uploaded_data.csv', 'wb') as f:
            #     f.write(uploaded_file.getvalue())
            st.sidebar.success("Upload Successful")
        except Exception as e:
            st.sidebar.error(f"Error uploading file: {e}")
            df = load_data()
    else:
        try:
            df = load_data()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.error("Please make sure 'supermarket_sales.csv' exists in the current directory.")
            st.stop()

    # Title and description
    st.title("📊 RFM Analysis Dashboard")
    st.markdown("""
    This dashboard analyzes customer behavior using RFM (Recency, Frequency, Monetary) metrics:
    * **Recency**: Days since last purchase
    * **Frequency**: Number of purchases
    * **Monetary**: Total spending
    """)

    # Sidebar filters for date and transaction amount
    st.sidebar.header("Filters")

    # Use try-except for date range
    try:
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(df['Date'].min().date(), df['Date'].max().date()),
            min_value=df['Date'].min().date(),
            max_value=df['Date'].max().date(),
            key='date_range_filter'
        )
    except Exception as e:
        st.sidebar.error(f"Error with date input: {e}")
        st.stop()

    # Use try-except for slider
    try:
        transaction_amount = st.sidebar.slider(
            "Transaction Amount Range",
            min_value=float(df['Total'].min()),
            max_value=float(df['Total'].max()),
            value=(float(df['Total'].min()), float(df['Total'].max())),
            key='transaction_amount_slider'
        )
    except Exception as e:
        st.sidebar.error(f"Error with slider: {e}")
        st.stop()

    # Filter data based on user input
    filtered_df = df[
        (df['Date'] >= pd.to_datetime(date_range[0])) & 
        (df['Date'] <= pd.to_datetime(date_range[1])) &
        (df['Total'].between(transaction_amount[0], transaction_amount[1]))
    ]

    # Check if filtered dataframe is empty
    if filtered_df.empty:
        st.warning("No data matches the current filters. Please adjust your selection.")
        st.stop()

    # RFM Calculation
    current_date = filtered_df['Date'].max()

    # Use a simpler approach for groupby to avoid Arrow serialization issues
    # First, get unique invoice IDs
    invoice_ids = filtered_df['Invoice ID'].unique()

    # Create empty lists to store results
    recency_values = []
    frequency_values = []
    monetary_values = []
    invoice_id_list = []

    # Calculate RFM manually
    for invoice_id in invoice_ids:
        invoice_data = filtered_df[filtered_df['Invoice ID'] == invoice_id]
        
        # Calculate recency
        latest_date = invoice_data['Date'].max()
        recency = (current_date - latest_date).days
        
        # Calculate frequency (number of transactions)
        frequency = len(invoice_data)
        
        # Calculate monetary (total spending)
        monetary = invoice_data['Total'].sum()
        
        # Append to lists
        invoice_id_list.append(invoice_id)
        recency_values.append(recency)
        frequency_values.append(frequency)
        monetary_values.append(monetary)

    # Create RFM DataFrame
    rfm_data = {
        'Invoice ID': invoice_id_list,
        'Recency': recency_values,
        'Frequency': frequency_values,
        'Monetary': monetary_values
    }
    rfm = pd.DataFrame(rfm_data)

    # Define bin edges for Recency, Frequency, and Monetary
    recency_bins = [0, 30, 90, 180, 365]  # Example bins for Recency
    frequency_bins = [1, 2, 5, 10, 20]    # Example bins for Frequency
    monetary_bins = [0, 500, 1000, 5000, 10000]  # Example bins for Monetary

    # Assign labels for the bins
    recency_labels = ['1', '2', '3', '4']
    frequency_labels = ['4', '3', '2', '1']
    monetary_labels = ['4', '3', '2', '1']

    # Segmenting with pd.cut and handle missing values with try-except
    try:
        rfm['R'] = pd.cut(rfm['Recency'], bins=recency_bins, labels=recency_labels, include_lowest=True)
        rfm['F'] = pd.cut(rfm['Frequency'], bins=frequency_bins, labels=frequency_labels, include_lowest=True)
        rfm['M'] = pd.cut(rfm['Monetary'], bins=monetary_bins, labels=monetary_labels, include_lowest=True)
        
        # Convert to string to avoid issues with Arrow serialization
        rfm['R'] = rfm['R'].astype(str)
        rfm['F'] = rfm['F'].astype(str)
        rfm['M'] = rfm['M'].astype(str)
        
        # Replace nan values
        rfm['R'] = rfm['R'].replace('nan', 'Other')
        rfm['F'] = rfm['F'].replace('nan', 'Other')
        rfm['M'] = rfm['M'].replace('nan', 'Other')
    except Exception as e:
        st.error(f"Error creating RFM segments: {e}")

    # Add RFM combined score
    rfm['RFM_Score'] = rfm['R'] + rfm['F'] + rfm['M']
    
    # Add customer segment based on RFM score
    def assign_segment(row):
        score = row['RFM_Score']
        r_score = int(row['R']) if row['R'] != 'Other' else 0
        f_score = int(row['F']) if row['F'] != 'Other' else 0
        m_score = int(row['M']) if row['M'] != 'Other' else 0
        
        # Loyal Customers
        if r_score >= 2 and f_score >= 3 and m_score >= 3:
            return 'Loyal Customers'
        # At Risk
        elif r_score <= 2 and f_score >= 2:
            return 'At Risk'
        # New Customers (1-2 purchases)
        elif frequency_values[invoice_id_list.index(row['Invoice ID'])] <= 2:
            return 'New Customers'
        else:
            return 'Others'
    
    # Apply the segment function
    rfm['Segment'] = rfm.apply(assign_segment, axis=1)

    # Create dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Data Explorer", "Customer Segments", "About"])
    
    with tab1:
        # Calculate and display metrics
        total_customers = len(rfm)
        average_recency = np.mean(rfm['Recency'])
        average_frequency = np.mean(rfm['Frequency'])
        average_monetary = np.mean(rfm['Monetary'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", total_customers)
        col2.metric("Average Recency", f"{average_recency:.2f} days")
        col3.metric("Average Frequency", f"{average_frequency:.2f} purchases")
        col4.metric("Average Monetary", f"${average_monetary:.2f}")

        # Customer segments pie chart
        try:
            st.subheader("Customer Segment Distribution")
            segment_counts = rfm['Segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            
            fig_segment = px.pie(
                segment_counts, 
                values='Count', 
                names='Segment', 
                title='Customer Segments Distribution',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig_segment, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating segment pie chart: {e}")

        # 3D visualization
        try:
            st.subheader("3D RFM Visualization")
            # Sample data if too large for 3D plot
            if len(rfm) > 1000:
                sample_rfm = rfm.sample(1000, random_state=42)
                fig_3d = px.scatter_3d(
                    sample_rfm, x='Recency', y='Frequency', z='Monetary', 
                    color='Segment',
                    title="3D Visualization of RFM Metrics (1000 sample points)"
                )
            else:
                fig_3d = px.scatter_3d(
                    rfm, x='Recency', y='Frequency', z='Monetary', 
                    color='Segment',
                    title="3D Visualization of RFM Metrics"
                )
            st.plotly_chart(fig_3d, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating 3D scatter plot: {e}")
    
    with tab2:
        st.subheader("RFM Data Explorer")
        
        # Search and filter options
        search_col, filter_col = st.columns(2)
        
        with search_col:
            search_term = st.text_input("Search by Invoice ID", "")
        
        with filter_col:
            segment_filter = st.multiselect(
                "Filter by Segment",
                options=['All'] + list(rfm['Segment'].unique()),
                default=['All']
            )
        
        # Apply filters
        filtered_rfm = rfm.copy()
        
        if search_term:
            filtered_rfm = filtered_rfm[filtered_rfm['Invoice ID'].str.contains(search_term, case=False)]
        
        if segment_filter and 'All' not in segment_filter:
            filtered_rfm = filtered_rfm[filtered_rfm['Segment'].isin(segment_filter)]
        
        # Data table
        st.markdown("### RFM Data")
        # Convert to HTML to display without using st.dataframe or st.write
        rfm_html = filtered_rfm.head(50).to_html(index=False)
        st.markdown(rfm_html, unsafe_allow_html=True)
        
        # Export options
        st.subheader("Export Data")
        try:
            csv_data = filtered_rfm.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Filtered RFM Data",
                csv_data,
                "rfm_filtered_data.csv",
                "text/csv",
                key='download_csv_button'
            )
        except Exception as e:
            st.error(f"Error creating download button: {e}")
    
    with tab3:
        st.subheader("Customer Segmentation Analysis")
        
        # Segment description
        segment_descriptions = {
            "Loyal Customers": "Consistent and dependable customers",
            "New Customers": "Customers who purchased recently but not made many purchases as yet",
            "At Risk": "Customers who haven't purchased recently",
        }
        
        # Segment metrics
        segment_metrics = rfm.groupby('Segment').agg({
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean',
            'Invoice ID': 'count'
        }).reset_index()
        
        segment_metrics = segment_metrics.rename(columns={
            'Invoice ID': 'Count',
            'Recency': 'Avg Days Since Purchase',
            'Frequency': 'Avg Purchase Frequency',
            'Monetary': 'Avg Spend ($)'
        })
        
        # Format metrics
        segment_metrics['Avg Days Since Purchase'] = segment_metrics['Avg Days Since Purchase'].round(1)
        segment_metrics['Avg Purchase Frequency'] = segment_metrics['Avg Purchase Frequency'].round(1)
        segment_metrics['Avg Spend ($)'] = segment_metrics['Avg Spend ($)'].round(2)
        
        # Add "New Customers" to the segment options if not already there
        segment_options = segment_metrics['Segment'].tolist()
        if 'New Customers' not in segment_options:
            segment_options.append('New Customers')
            
        # Display segment details
        selected_segment = st.selectbox(
            "Select Customer Segment to Analyze",
            options=segment_options
        )
        
        # Check if we need to handle New Customers separately
        if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
            # Filter for only new customers (1-2 purchases)
            new_customers = rfm[rfm['Frequency'] <= 2]
            
            # Calculate basic metrics for New Customers
            new_customers_count = len(new_customers)
            avg_recency = np.mean(new_customers['Recency']) if len(new_customers) > 0 else 0
            avg_frequency = np.mean(new_customers['Frequency']) if len(new_customers) > 0 else 0
            avg_monetary = np.mean(new_customers['Monetary']) if len(new_customers) > 0 else 0
            
            st.markdown(f"### {selected_segment}")
            st.markdown(f"**Description**: {segment_descriptions.get(selected_segment, 'Customers who purchased recently but not made many purchases as yet')}")
        else:
            # Display regular segment info
            segment_data = segment_metrics[segment_metrics['Segment'] == selected_segment].iloc[0]
            
            st.markdown(f"### {selected_segment}")
            st.markdown(f"**Description**: {segment_descriptions.get(selected_segment, 'No description available')}")
        
        # Metrics for the selected segment
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
            # Show metrics for new customers
            with metric_col1:
                st.metric("Number of Customers", new_customers_count)
            
            with metric_col2:
                st.metric("Avg Days Since Purchase", f"{avg_recency:.2f} days")
            
            with metric_col3:
                st.metric("Avg Purchase Frequency", f"{avg_frequency:.2f}")
            
            with metric_col4:
                st.metric("Avg Spend ($)", f"${avg_monetary:.2f}")
        else:
            # Show regular segment metrics
            with metric_col1:
                st.metric("Number of Customers", int(segment_data['Count']))
            
            with metric_col2:
                st.metric("Avg Days Since Purchase", segment_data['Avg Days Since Purchase'])
            
            with metric_col3:
                st.metric("Avg Purchase Frequency", segment_data['Avg Purchase Frequency'])
            
            with metric_col4:
                st.metric("Avg Spend ($)", f"${segment_data['Avg Spend ($)']}")
        
        # RFM Distribution for the segment
        try:
            if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
                # Show distribution for new customers
                if len(new_customers) > 0:
                    fig_box = go.Figure()
                    fig_box.add_trace(go.Box(y=new_customers['Recency'], name="Recency"))
                    fig_box.add_trace(go.Box(y=new_customers['Frequency'], name="Frequency"))
                    fig_box.add_trace(go.Box(y=new_customers['Monetary'], name="Monetary"))
                    fig_box.update_layout(title=f"Distribution of RFM Metrics for {selected_segment}")
                    st.plotly_chart(fig_box, use_container_width=True)
                else:
                    st.warning("No new customers found in the current data selection.")
            else:
                # Show regular segment distribution
                segment_rfm = rfm[rfm['Segment'] == selected_segment]
                
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(y=segment_rfm['Recency'], name="Recency"))
                fig_box.add_trace(go.Box(y=segment_rfm['Frequency'], name="Frequency"))
                fig_box.add_trace(go.Box(y=segment_rfm['Monetary'], name="Monetary"))
                fig_box.update_layout(title=f"Distribution of RFM Metrics for {selected_segment}")
                st.plotly_chart(fig_box, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating box plot: {e}")
        
        # Marketing recommendations based on segment
        st.subheader("Marketing Recommendations")
        
        recommendations = {
           
            "Loyal Customers": [
                "tip 1",
                "tip 2",
                "tip 3",
                "tip 4"
            ],
            "New Customers": [
                 "tip 1",
                "tip 2",
                "tip 3",
                "tip 4"
            ],
            "At Risk": [
                "tip 1",
                "tip 2",
                "tip 3",
                "tip 4"
            ],
            
        }
        
        segment_recommendations = recommendations.get(selected_segment, ["No specific recommendations available for this segment"])
        
        for i, rec in enumerate(segment_recommendations, 1):
            st.markdown(f"**{i}. {rec}**")
            
        # Add data table and export option for New Customers
        if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
            st.subheader("New Customer Data")
            
            if len(new_customers) > 0:
                # Display the first 50 rows as HTML
                rfm_html = new_customers.head(50).to_html(index=False)
                st.markdown(rfm_html, unsafe_allow_html=True)
                
                # Export options
                st.subheader("Export Data")
                try:
                    csv_data = new_customers.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download New Customer Data",
                        csv_data,
                        "new_customers_data.csv",
                        "text/csv",
                        key='download_new_customer_button'
                    )
                except Exception as e:
                    st.error(f"Error creating download button: {e}")
            else:
                st.info("No new customer data available to display.")
    
    # About Tab
    with tab4:
        st.title("About RFM Analysis")
        st.markdown("""
        This section provides information about RFM analysis, its benefits, and how to use this dashboard.
        """)
        
        # Create expandable sections for each category
        with st.expander("What is RFM Analysis?"):
            st.markdown("*Fill in details about what RFM analysis is and how it works...*")
        
        with st.expander("Benefits of RFM Segmentation"):
            st.markdown("*Fill in details about the benefits of using RFM for customer segmentation...*")
        
        with st.expander("How to Interpret RFM Scores"):
            st.markdown("*Fill in details about how to interpret the RFM scores and segments...*")
        
        with st.expander("How This Application Drives Business Success"):
            st.markdown("*Fill in details about how this dashboard helps implement RFM analysis for business growth and success...*")
    


# Initialize users database
initialize_users()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# Check if user is authenticated
if st.session_state["authenticated"]:
    main()
else:
    auth_page()
