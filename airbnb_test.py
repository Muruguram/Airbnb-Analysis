import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Function to upload and read CSV
def load_data():
    uploaded_file = st.file_uploader("Upload Airbnb Data CSV", type=['csv'])
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        st.warning("Please upload a CSV file to proceed.")
        return None

# Load data
df = load_data()
if df is None:
    st.stop()

# Streamlit UI
st.title("Airbnb Data Analysis Dashboard")
tabs = st.tabs([
    "🏠 Introduction", "📊 Data Overview", "📈 Insights & Visualizations", "📅 Availability Analysis", "🌍 Geo Analysis"
])

with tabs[0]:
    st.header("Welcome to the Airbnb Analysis Dashboard")
    st.write("""
    This dashboard helps analyze Airbnb data, focusing on pricing trends, availability, and market insights.
    """)

with tabs[1]:
    st.header("Data Overview")
    st.dataframe(df.head())
    st.write(f"Total Rows: {df.shape[0]}, Total Columns: {df.shape[1]}")

with tabs[2]:
    st.header("Insights & Visualizations")
    options = [
        "Room Type Distribution", "Price vs. Number of Reviews", "Most Common Property Types",
        "Impact of Availability on Pricing", "Top 10 Host Names Overall",
        "Top 10 Listings by Price", "Top 10 Countries by Listings", "Correlation Heatmap"
    ]
    choice = st.selectbox("Select an Insight", options)

    if choice == "Room Type Distribution":
        fig = px.pie(df, names='room_type', title='Room Type Distribution')
        st.plotly_chart(fig)

    elif choice == "Price vs. Number of Reviews":
        fig = px.scatter(df, x='price', y='number_of_reviews', title='Price vs. Number of Reviews')
        st.plotly_chart(fig)

    elif choice == "Most Common Property Types":
        prop_counts = df['property_type'].value_counts().reset_index()
        prop_counts.columns = ['property_type', 'count']
        fig = px.bar(prop_counts, x='property_type', y='count', title='Most Common Property Types')
        st.plotly_chart(fig)

    elif choice == "Impact of Availability on Pricing":
        fig = px.scatter(df, x='availability_365', y='price', title='Availability vs. Price')
        st.plotly_chart(fig)

    elif choice == "Top 10 Host Names Overall":
        if 'host_name' in df.columns and 'country' in df.columns:
            top_hosts = df.groupby(['host_name', 'country']).size().reset_index(name='listing_count')
            top_hosts = top_hosts.sort_values(by='listing_count', ascending=False).head(10)
            st.dataframe(top_hosts)
            fig = px.bar(top_hosts, x='host_name', y='listing_count', color='country', title='Top 10 Host Names Overall')
            st.plotly_chart(fig)
        else:
            st.error("The dataset does not contain 'host_name' or 'country' columns.")
    
    elif choice == "Top 10 Listings by Price":
        top_listings = df.nlargest(10, 'price')
        fig = px.bar(top_listings, x='name', y='price', title='Top 10 Listings by Price')
        st.plotly_chart(fig)
    
    elif choice == "Top 10 Countries by Listings":
        if 'country' in df.columns:
            country_counts = df['country'].value_counts().nlargest(10).reset_index()
            country_counts.columns = ['country', 'count']
            fig = px.bar(country_counts, x='country', y='count', title='Top 10 Countries by Listings')
            st.plotly_chart(fig)
        else:
            st.error("The dataset does not contain a 'country' column.")
    
    elif choice == "Correlation Heatmap":
        st.write("The heatmap shows the correlation between different numerical features in the dataset.")
        fig, ax = plt.subplots(figsize=(10, 6))
        correlation_matrix = df.select_dtypes(include=['number']).corr()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        st.pyplot(fig)

with tabs[3]:
    st.header("Availability Analysis")
    if {'availability_30', 'availability_60', 'availability_90', 'room_type'}.issubset(df.columns):
        availability_30 = df.groupby('room_type')['availability_30'].mean().reset_index()
        availability_60 = df.groupby('room_type')['availability_60'].mean().reset_index()
        availability_90 = df.groupby('room_type')['availability_90'].mean().reset_index()
        
        fig1 = px.pie(availability_30, names='room_type', values='availability_30', title="30-Day Availability by Room Type")
        st.plotly_chart(fig1)
        
        fig2 = px.pie(availability_60, names='room_type', values='availability_60', title="60-Day Availability by Room Type")
        st.plotly_chart(fig2)
        
        fig3 = px.pie(availability_90, names='room_type', values='availability_90', title="90-Day Availability by Room Type")
        st.plotly_chart(fig3)
    else:
        st.error("The dataset does not contain necessary columns for availability analysis.")

with tabs[4]:
    st.header("Geo Analysis")
    if 'country' in df.columns and 'availability_365' in df.columns:
        price_range = st.sidebar.slider("Select Price Range", int(df["price"].min()), int(df["price"].max()), (int(df["price"].min()), int(df["price"].max())))
        df_filtered = df[(df["price"] >= price_range[0]) & (df["price"] <= price_range[1])]
        
        st.dataframe(df_filtered[['country', 'price', 'room_type', 'property_type']])
        
        country_df = df_filtered.groupby('country', as_index=False)['availability_365'].mean()
        country_df['availability_365'] = country_df['availability_365'].astype(int)
        fig = px.scatter_geo(
            data_frame=country_df,
            locations='country',
            color='availability_365',
            hover_data=['availability_365'],
            locationmode='country names',
            size='availability_365',
            title='Avg Availability in Selected Price Range',
            color_continuous_scale='agsunset'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("The dataset does not contain necessary country or availability columns.")
