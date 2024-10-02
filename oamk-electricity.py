"""
Streamlit application for analyzing energy consumption and bills.
"""

import pandas as pd
import streamlit as st

# Load the datasets
ELECTRICITY_DATA_PATH = 'data/Electricity_20-09-2024.csv'
PRICE_DATA_PATH = 'data/sahkon-hinta-010121-240924.csv'

# Read the data from CSV files
electricity_df = pd.read_csv(ELECTRICITY_DATA_PATH, sep=';')
price_df = pd.read_csv(PRICE_DATA_PATH)

# Clean data: Convert string numbers with commas to floats
electricity_df['Energy (kWh)'] = electricity_df['Energy (kWh)'].str.replace(',', '.').astype(float)
electricity_df['Temperature'] = electricity_df['Temperature'].str.replace(',', '.').astype(float)

# Remove any leading/trailing whitespace from the 'Time' column in electricity_df
electricity_df['Time'] = electricity_df['Time'].str.strip()

# Convert 'Time' columns in both dataframes to Pandas datetime
electricity_df['Time'] = pd.to_datetime(electricity_df['Time'].str.strip(), format='%d.%m.%Y %H:%M')
price_df['Time'] = pd.to_datetime(price_df['Time'], format='%d-%m-%Y %H:%M:%S')

electricity_df = electricity_df.drop_duplicates(subset='Time')
price_df = price_df.drop_duplicates(subset='Time')

# Merge the dataframes based on the 'Time' column
merged_df = pd.merge(
    electricity_df[['Time', 'Energy (kWh)', 'Temperature']],
    price_df, on='Time',
    how='inner', validate='1:1'
)

# Calculate the hourly bill paid (Price * Energy / 100 to convert to EUR)
merged_df['Bill (EUR)'] = (merged_df['Price (cent/kWh)'] * merged_df['Energy (kWh)']) / 100

# Function to group data based on a selected interval (daily, weekly, or hourly)
def group_data(grouping_interval: str) -> pd.DataFrame:
    """
    Groups the merged data based on the selected time interval.

    Args:
        grouping_interval (str): The interval for grouping (Daily, Weekly, Hourly).
    
    Returns:
        pd.DataFrame: The grouped dataframe.
    """
    if grouping_interval == "Daily":
        grouped = merged_df.resample('D', on='Time').agg({
            'Energy (kWh)': 'sum',
            'Bill (EUR)': 'sum',
            'Price (cent/kWh)': 'mean',
            'Temperature': 'mean'
        })
    elif grouping_interval == "Weekly":
        grouped = merged_df.resample('W', on='Time').agg({
            'Energy (kWh)': 'sum',
            'Bill (EUR)': 'sum',
            'Price (cent/kWh)': 'mean',
            'Temperature': 'mean'
        })
    elif grouping_interval == "Hourly":
        grouped = merged_df.resample('H', on='Time').agg({
            'Energy (kWh)': 'sum',
            'Bill (EUR)': 'sum',
            'Price (cent/kWh)': 'mean',
            'Temperature': 'mean'
        })
    else:
        raise ValueError(f"Unknown interval: {grouping_interval}")

    return grouped

# Example of grouping by daily interval
#grouped_daily = group_data("Daily")
#grouped_weekly = group_data("Weekly")
#grouped_hourly = group_data("Hourly")

# Streamlit App starts here

# Set the title for the Streamlit app
st.title('Energy Consumption and Bill Analysis')

# Selector for grouping interval
interval = st.selectbox('Select the grouping interval', ('Hourly', 'Daily', 'Weekly'))

# Apply the selected grouping
grouped_data = group_data(interval)

# Selector for date range to analyze
start_date = st.date_input('Select start date', pd.to_datetime(grouped_data.index.min()))
end_date = st.date_input('Select end date', pd.to_datetime(grouped_data.index.max()))

# Filter data based on the selected date range
filtered_data = grouped_data.loc[start_date:end_date]
price_range = filtered_data["Price (cent/kWh)"].max() - filtered_data["Price (cent/kWh)"].min()
energy_to_bill_ratio = filtered_data["Energy (kWh)"].sum() / filtered_data["Bill (EUR)"].sum()
consumption_per_degree = filtered_data["Energy (kWh)"].sum() / filtered_data["Temperature"].mean()

# Line chart for consumption, bill, price, and temperature
st.line_chart(filtered_data[['Energy (kWh)', 'Bill (EUR)', 'Price (cent/kWh)', 'Temperature']])

# Display some statistics
st.write(f'Analysis from {start_date} to {end_date}')
st.write(f'Total consumption: {filtered_data["Energy (kWh)"].sum()} kWh')
st.write(f'Total bill: {filtered_data["Bill (EUR)"].sum()} EUR')
st.write(f'Average price: {filtered_data["Price (cent/kWh)"].mean()} cents/kWh')
st.write(f'Day with highest average price: {filtered_data["Price (cent/kWh)"].idxmax()}')
st.write(f'Average temperature: {filtered_data["Temperature"].mean()} °C')
st.write(f'Median consumption: {filtered_data["Energy (kWh)"].median()} kWh')
st.write(f'Median bill: {filtered_data["Bill (EUR)"].median()} EUR')
st.write(f'Median price: {filtered_data["Price (cent/kWh)"].median()} cents/kWh')
st.write(f'Median temperature: {filtered_data["Temperature"].median()} °C')
st.write(f'Maximum consumption: {filtered_data["Energy (kWh)"].max()} kWh')
st.write(f'Minimum consumption: {filtered_data["Energy (kWh)"].min()} kWh')
st.write(f'Maximum bill: {filtered_data["Bill (EUR)"].max()} EUR')
st.write(f'Minimum bill: {filtered_data["Bill (EUR)"].min()} EUR')
st.write(f'Maximum price: {filtered_data["Price (cent/kWh)"].max()} cents/kWh')
st.write(f'Minimum price: {filtered_data["Price (cent/kWh)"].min()} cents/kWh')
st.write(f'Maximum temperature: {filtered_data["Temperature"].max()} °C')
st.write(f'Minimum temperature: {filtered_data["Temperature"].min()} °C')
st.write(f'Standard deviation of consumption: {filtered_data["Energy (kWh)"].std()} kWh')
st.write(f'Standard deviation of bill: {filtered_data["Bill (EUR)"].std()} EUR')
st.write(f'Standard deviation of price: {filtered_data["Price (cent/kWh)"].std()} cents/kWh')
st.write(f'Standard deviation of temperature: {filtered_data["Temperature"].std()} °C')
st.write(f'Total number of {interval.lower()} periods: {len(filtered_data)}')
st.write(f'Hour/Day with peak consumption: {filtered_data["Energy (kWh)"].idxmax()}')
st.write(f'Peak consumption: {filtered_data["Energy (kWh)"].max()} kWh')
st.write(f'Energy-to-bill efficiency: {energy_to_bill_ratio:.2f} kWh per EUR')
st.write(f'Energy consumption per degree Celsius: {consumption_per_degree:.2f} kWh/°C')
st.write(f'Price variability: {price_range} cents/kWh')
