import pytz
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

# API Details
API_Key = "2912c64e912f42c94efafdd0ab7e2fb9"
city_list = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
CSV_FILE = "weather_data.csv"

# Get IST timezone
IST = pytz.timezone("Asia/Kolkata")

# Function to fetch weather data for a single city
def fetch_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_Key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # Get current IST time
        ist_now = datetime.now(IST)
        
        weather_info = {
            "timestamp": ist_now.strftime("%Y-%m-%d %H:%M:%S"),  # Store as IST-formatted string
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "city": city
        }
        return weather_info
    else:
        st.error(f"Failed to fetch data for {city}: {response.status_code}")
        return None

# Function to fetch and store data for the selected city
def fetch_and_store_selected_city(selected_city):
    weather_data = fetch_weather_data(selected_city)
    if weather_data:
        df = pd.DataFrame([weather_data])
        df.to_csv(CSV_FILE, mode="a", index=False, header=not os.path.exists(CSV_FILE))

# Auto-refresh every 5 minutes (300,000 ms)
st_autorefresh(interval=300000, limit=None, key="autorefresh")

# App UI
st.title("🌏 Live Weather Dashboard ")

# Dropdown to select city
selected_city = st.selectbox("Select a City", city_list)

# Trigger data collection for the selected city
fetch_and_store_selected_city(selected_city)

# Load and display data
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    
    # Ensure timestamps are correctly parsed and converted to IST
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")
    df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Kolkata", ambiguous='NaT', nonexistent='NaT')  # Explicitly set to IST

    # Filter data for the selected city
    city_data = df[df["city"] == selected_city]

    if not city_data.empty:
        # Display latest weather info
        latest_data = city_data.iloc[-1]

        st.write("### Current Weather:")
        st.write(f"- **🌡️ Temperature:** {latest_data['temperature']}°C")
        st.write(f"- **💧 Humidity:** {latest_data['humidity']}%")
        st.write(f"- **🌬️ Wind Speed:** {latest_data['wind_speed']} m/s")
        st.write(f"- **🌥️ Description:** {latest_data['description']}")
        st.write(f"- **📅 Date & Time (IST):** {latest_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        # Temperature over time visualization
        st.write("### 📈 **Temperature Over Time :**")
        fig_temp = px.line(
            city_data, 
            x="timestamp",
            y="temperature",
            color="city", 
            title="Temperature Over Time",
            labels={"timestamp": "Time", "temperature": "Temperature (°C)"},
            color_discrete_sequence=["#1E90FF"]
        )
        fig_temp.update_layout(
            plot_bgcolor="black", 
            paper_bgcolor="black",
            font=dict(color="white")
        )
        st.plotly_chart(fig_temp)

        # Humidity over time visualization
        st.write("### 🌊 **Humidity Over Time :**")
        fig_humidity = px.line(
            city_data, 
            x="timestamp", 
            y="humidity", 
            color="city",  
            title="Humidity Trends",
            labels={"timestamp": "Time ", "humidity": "Humidity (%)"},
            color_discrete_sequence=["#FF6347"]
        )
        fig_humidity.update_layout(
            plot_bgcolor="black", 
            paper_bgcolor="black",
            font=dict(color="white")
        )
        st.plotly_chart(fig_humidity)

    else:
        st.write("No data available for the selected city.")
else:
    st.write("No weather data available. Fetching data...")

# Footer
st.write("🌟 This app fetches and stores data in **Indian Standard Time (IST)**. 🌟")
