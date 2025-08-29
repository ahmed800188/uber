import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Uber color palette
UBER_BLACK = '#000000'
UBER_ORANGE = '#FF5A1F'
UBER_WHITE = '#FFFFFF'
UBER_GRAY = '#E5E5E5'

st.set_page_config(page_title='Uber NCR Dashboard', page_icon='🚗', layout='wide', initial_sidebar_state='expanded',
                   menu_items={'About': 'Uber Data Analysis Dashboard'})

# Custom Uber banner
st.markdown(f"""
    <div style='background-color:{UBER_BLACK};padding:20px;border-radius:10px;margin-bottom:20px;'>
        <h1 style='color:{UBER_ORANGE};text-align:center;'>🚗 Uber NCR Ride Bookings Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# Read the CSV file
csv_path = 'ncr_ride_bookings.csv'
df = pd.read_csv(csv_path)

# Remove extra quotes from IDs
id_cols = ['Booking ID', 'Customer ID']
for col in id_cols:
    df[col] = df[col].astype(str).str.replace('"', '').str.strip()

# Convert 'Date' and 'Time' to datetime
# Combine into a single datetime column
if 'Date' in df.columns and 'Time' in df.columns:
    df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
    df.drop(['Date', 'Time'], axis=1, inplace=True)

# Convert numeric columns
numeric_cols = ['Avg VTAT', 'Avg CTAT', 'Booking Value', 'Ride Distance', 'Driver Ratings', 'Customer Rating']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Replace 'null' strings with np.nan
for col in df.columns:
    df[col] = df[col].replace('null', np.nan)

# Strip whitespace from string columns
for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].str.strip()

# Drop duplicates
df.drop_duplicates(inplace=True)

# Sidebar for navigation and filters
with st.sidebar:
    st.markdown(f"<h2 style='color:{UBER_ORANGE};'>Navigation</h2>", unsafe_allow_html=True)
    page = st.radio('Go to', ['Key Metrics', 'Booking Status', 'Ride Distance', 'Booking Value by Vehicle', 'Monthly Trends', 'Raw Data'])
    st.markdown(f"<hr style='border:1px solid {UBER_ORANGE};' />", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{UBER_ORANGE};'>Filters</h3>", unsafe_allow_html=True)
    vehicle_types = st.multiselect('Vehicle Type', options=df['Vehicle Type'].dropna().unique(), default=list(df['Vehicle Type'].dropna().unique()))
    status_types = st.multiselect('Booking Status', options=df['Booking Status'].dropna().unique(), default=list(df['Booking Status'].dropna().unique()))

filtered_df = df[df['Vehicle Type'].isin(vehicle_types) & df['Booking Status'].isin(status_types)]

st.markdown(f"<style>body {{background-color: {UBER_WHITE}; color: {UBER_BLACK};}} .stApp {{background-color: {UBER_WHITE};}} .stSidebar {{background-color: {UBER_GRAY};}} </style>", unsafe_allow_html=True)

if page == 'Key Metrics':
    st.markdown(f"<h2 style='color:{UBER_ORANGE};'>Key Metrics</h2>", unsafe_allow_html=True)
    with st.container():
        total_rides = len(filtered_df)
        completed_rides = (filtered_df['Booking Status'] == 'Completed').sum()
        cancelled_rides = ((filtered_df['Booking Status'] == 'Cancelled by Driver') | (filtered_df['Booking Status'] == 'Cancelled by Customer')).sum()
        avg_driver_rating = filtered_df['Driver Ratings'].mean()
        avg_customer_rating = filtered_df['Customer Rating'].mean()
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric('Total Rides', total_rides)
        col2.metric('Completed Rides', completed_rides)
        col3.metric('Cancelled Rides', cancelled_rides)
        col4.metric('Avg Driver Rating', f"{avg_driver_rating:.2f}")
        col5.metric('Avg Customer Rating', f"{avg_customer_rating:.2f}")
    st.markdown(f"<hr style='border:1px solid {UBER_ORANGE};' />", unsafe_allow_html=True)
    with st.expander('Booking Status Pie Chart', expanded=True):
        fig1, ax1 = plt.subplots()
        status_counts = filtered_df['Booking Status'].value_counts()
        ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=[UBER_ORANGE, UBER_BLACK, UBER_GRAY, UBER_WHITE], textprops={'color': UBER_BLACK})
        ax1.set_facecolor(UBER_WHITE)
        st.pyplot(fig1)
    # Line chart for total rides per month
    st.markdown(f"<h4 style='color:{UBER_ORANGE};'>Total Rides Per Month (Line Chart)</h4>", unsafe_allow_html=True)
    filtered_df['month'] = filtered_df['datetime'].dt.to_period('M').astype(str)
    monthly_total = filtered_df.groupby('month').size()
    fig_line, ax_line = plt.subplots()
    monthly_total.plot(kind='line', color=UBER_ORANGE, marker='o', ax=ax_line)
    ax_line.set_xlabel('Month')
    ax_line.set_ylabel('Total Rides')
    ax_line.set_facecolor(UBER_WHITE)
    st.pyplot(fig_line)

elif page == 'Booking Status':
    st.markdown(f"<h2 style='color:{UBER_ORANGE};'>Booking Status Distribution</h2>", unsafe_allow_html=True)
    with st.container():
        status_counts = filtered_df['Booking Status'].value_counts()
        fig, ax = plt.subplots()
        sns.barplot(x=status_counts.index, y=status_counts.values, ax=ax, palette=[UBER_ORANGE, UBER_BLACK, UBER_GRAY, UBER_WHITE])
        ax.set_xlabel('Booking Status')
        ax.set_ylabel('Count')
        ax.set_facecolor(UBER_WHITE)
        st.pyplot(fig)
    st.markdown(f"<hr style='border:1px solid {UBER_ORANGE};' />", unsafe_allow_html=True)
    with st.expander('Booking Status Pie Chart', expanded=True):
        fig2, ax2 = plt.subplots()
        ax2.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=[UBER_ORANGE, UBER_BLACK, UBER_GRAY, UBER_WHITE], textprops={'color': UBER_BLACK})
        ax2.set_facecolor(UBER_WHITE)
        st.pyplot(fig2)
    # Line chart for Booking Status over months
    st.markdown(f"<h4 style='color:{UBER_ORANGE};'>Booking Status Over Time (Line Chart)</h4>", unsafe_allow_html=True)
    filtered_df['month'] = filtered_df['datetime'].dt.to_period('M').astype(str)
    status_monthly = filtered_df.groupby(['month', 'Booking Status']).size().unstack(fill_value=0)
    fig_line, ax_line = plt.subplots()
    status_monthly.plot(kind='line', ax=ax_line, color=[UBER_ORANGE, UBER_BLACK, UBER_GRAY, UBER_WHITE])
    ax_line.set_xlabel('Month')
    ax_line.set_ylabel('Count')
    ax_line.set_facecolor(UBER_WHITE)
    st.pyplot(fig_line)

elif page == 'Ride Distance':
    st.markdown(f"<h2 style='color:{UBER_ORANGE};'>Ride Distance Distribution</h2>", unsafe_allow_html=True)
    with st.container():
        fig, ax = plt.subplots()
        sns.histplot(filtered_df['Ride Distance'].dropna(), bins=30, color=UBER_ORANGE, ax=ax)
        ax.set_xlabel('Ride Distance (km)')
        ax.set_ylabel('Frequency')
        ax.set_facecolor(UBER_WHITE)
        st.pyplot(fig)
    st.markdown(f"<hr style='border:1px solid {UBER_ORANGE};' />", unsafe_allow_html=True)
    with st.expander('Ride Distance Bar Chart', expanded=True):
        fig2, ax2 = plt.subplots()
        ride_dist_counts = pd.cut(filtered_df['Ride Distance'].dropna(), bins=10).value_counts().sort_index()
        ride_dist_counts.plot(kind='bar', color=UBER_ORANGE, ax=ax2)
        ax2.set_xlabel('Ride Distance Range (km)')
        ax2.set_ylabel('Count')
        ax2.set_facecolor(UBER_WHITE)
        st.pyplot(fig2)
    # Line chart for average ride distance per month
    st.markdown(f"<h4 style='color:{UBER_ORANGE};'>Average Ride Distance Per Month (Line Chart)</h4>", unsafe_allow_html=True)
    filtered_df['month'] = filtered_df['datetime'].dt.to_period('M').astype(str)
    avg_dist_monthly = filtered_df.groupby('month')['Ride Distance'].mean()
    fig_line, ax_line = plt.subplots()
    avg_dist_monthly.plot(kind='line', color=UBER_ORANGE, marker='o', ax=ax_line)
    ax_line.set_xlabel('Month')
    ax_line.set_ylabel('Avg Ride Distance (km)')
    ax_line.set_facecolor(UBER_WHITE)
    st.pyplot(fig_line)

elif page == 'Booking Value by Vehicle':
    st.markdown(f"<h2 style='color:{UBER_ORANGE};'>Average Booking Value by Vehicle Type</h2>", unsafe_allow_html=True)
    with st.container():
        avg_value_by_vehicle = filtered_df.groupby('Vehicle Type')['Booking Value'].mean().sort_values()
        fig, ax = plt.subplots()
        avg_value_by_vehicle.plot(kind='bar', color=UBER_ORANGE, ax=ax)
        ax.set_xlabel('Vehicle Type')
        ax.set_ylabel('Avg Booking Value')
        ax.set_facecolor(UBER_WHITE)
        st.pyplot(fig)
    st.markdown(f"<hr style='border:1px solid {UBER_ORANGE};' />", unsafe_allow_html=True)
    with st.expander('Booking Value Pie Chart by Vehicle Type', expanded=True):
        fig2, ax2 = plt.subplots()
        vehicle_value_sum = filtered_df.groupby('Vehicle Type')['Booking Value'].sum()
        ax2.pie(vehicle_value_sum, labels=vehicle_value_sum.index, autopct='%1.1f%%', colors=[UBER_ORANGE, UBER_BLACK, UBER_GRAY, UBER_WHITE], textprops={'color': UBER_BLACK})
        ax2.set_facecolor(UBER_WHITE)
        st.pyplot(fig2)
    # Line chart for average booking value per month by vehicle type
    st.markdown(f"<h4 style='color:{UBER_ORANGE};'>Avg Booking Value Per Month by Vehicle Type (Line Chart)</h4>", unsafe_allow_html=True)
    filtered_df['month'] = filtered_df['datetime'].dt.to_period('M').astype(str)
    value_monthly = filtered_df.groupby(['month', 'Vehicle Type'])['Booking Value'].mean().unstack(fill_value=0)
    fig_line, ax_line = plt.subplots()
    value_monthly.plot(kind='line', ax=ax_line, color=[UBER_ORANGE, UBER_BLACK, UBER_GRAY, UBER_WHITE])
    ax_line.set_xlabel('Month')
    ax_line.set_ylabel('Avg Booking Value')
    ax_line.set_facecolor(UBER_WHITE)
    st.pyplot(fig_line)

elif page == 'Monthly Trends':
    st.markdown(f"<h2 style='color:{UBER_ORANGE};'>Monthly Ride Trends</h2>", unsafe_allow_html=True)
    with st.container():
        filtered_df['month'] = filtered_df['datetime'].dt.to_period('M').astype(str)
        monthly_trends = filtered_df.groupby('month').size()
        fig, ax = plt.subplots()
        monthly_trends.plot(kind='line', color=UBER_ORANGE, marker='o', ax=ax)
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Rides')
        ax.set_facecolor(UBER_WHITE)
        st.pyplot(fig)
    st.markdown(f"<hr style='border:1px solid {UBER_ORANGE};' />", unsafe_allow_html=True)
    with st.expander('Monthly Ride Bar Chart', expanded=True):
        fig2, ax2 = plt.subplots()
        monthly_trends.plot(kind='bar', color=UBER_ORANGE, ax=ax2)
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Number of Rides')
        ax2.set_facecolor(UBER_WHITE)
        st.pyplot(fig2)
    # Line chart for average driver rating per month
    st.markdown(f"<h4 style='color:{UBER_ORANGE};'>Avg Driver Rating Per Month (Line Chart)</h4>", unsafe_allow_html=True)
    avg_driver_rating_monthly = filtered_df.groupby('month')['Driver Ratings'].mean()
    fig_line, ax_line = plt.subplots()
    avg_driver_rating_monthly.plot(kind='line', color=UBER_ORANGE, marker='o', ax=ax_line)
    ax_line.set_xlabel('Month')
    ax_line.set_ylabel('Avg Driver Rating')
    ax_line.set_facecolor(UBER_WHITE)
    st.pyplot(fig_line)

elif page == 'Raw Data':
    st.markdown(f"<h2 style='color:{UBER_ORANGE};'>Raw Data</h2>", unsafe_allow_html=True)
    st.dataframe(filtered_df.head(100), height=600)
