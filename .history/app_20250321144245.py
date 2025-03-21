import streamlit as st
from datetime import datetime, timedelta
import time
import google.generativeai as genai

# Page setup
st.set_page_config(page_title="Smart Irrigation Assistant", page_icon="💧", layout="wide")

# Configure Gemini AI API
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Function to set custom styles
def set_custom_styles():
    st.markdown("""
        <style>
            body {
                background: url('https://source.unsplash.com/1600x900/?farm,field,nature') no-repeat center center fixed;
                background-size: cover;
            }
            .main-title {
                font-size: 36px;
                text-align: center;
                font-weight: bold;
                color: white;
                text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
            }
            .info-box {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
                box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.2);
                transition: transform 0.3s;
            }
            .info-box:hover {
                transform: scale(1.05);
            }
            .stButton>button {
                background: linear-gradient(135deg, #1E90FF, #00BFFF);
                color: white;
                font-size: 18px;
                padding: 12px 20px;
                border-radius: 8px;
                transition: 0.3s;
            }
        </style>
    """, unsafe_allow_html=True)

# Apply styles
set_custom_styles()

# Function to calculate water requirement
def calculate_water_requirement(soil, crop, weather, moisture_level):
    soil_factors = {"sandy": 1.5, "loamy": 1.0, "clay": 0.7, "peaty": 0.9, "saline": 1.2, "silty": 1.1}
    crop_factors = {"wheat": 1.0, "corn": 1.1, "rice": 1.3, "tomato": 1.2, "potato": 1.0, "banana": 1.5}
    weather_factors = {"hot": 1.3, "moderate": 1.0, "cold": 0.8}
    
    base_water = soil_factors.get(soil.lower(), 1.0)
    crop_adjustment = crop_factors.get(crop.lower(), 1.0)
    weather_adjustment = weather_factors.get(weather.lower(), 1.0)
    moisture_factor = 1.2 if moisture_level < 30 else 1.0 if moisture_level < 60 else 0.7

    return round(base_water * crop_adjustment * weather_adjustment * moisture_factor * 10, 2)

# Function to calculate harvest date
def calculate_harvest_date(crop, planting_date):
    crop_days = {"wheat": 120, "corn": 90, "rice": 150, "tomato": 80, "potato": 100, "banana": 180}
    days_to_harvest = crop_days.get(crop.lower(), 100)
    planting_date = datetime.strptime(planting_date, "%Y-%m-%d")
    return (planting_date + timedelta(days=days_to_harvest)).strftime("%Y-%m-%d")

# Function to get AI response
def chat_with_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# Title with animation
st.markdown('<h1 class="main-title">🌱 Smart Irrigation Assistant 💧</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar settings
st.sidebar.title("🔧 Customize Settings")
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])

if theme == "Dark":
    st.markdown("""
        <style>
            body { background-color: #1e1e1e; color: white; }
            .info-box { background: rgba(50, 50, 50, 0.9); color: white; }
        </style>
    """, unsafe_allow_html=True)

# Inputs for irrigation calculation
col1, col2 = st.columns(2)
with col1:
    soil = st.selectbox("🌱 Select Soil Type", ["Sandy", "Loamy", "Clay", "Peaty", "Saline", "Silty"])
    crop = st.selectbox("🌾 Select Crop Type", ["Wheat", "Corn", "Rice", "Tomato", "Potato", "Banana"])
with col2:
    planting_date = st.date_input("📅 Select Planting Date")
    weather = st.selectbox("☀️ Select Weather Condition", ["Hot", "Moderate", "Cold"])
    moisture_level = st.slider("💧 Soil Moisture Level (%)", 0, 100, 50)

# Button to get recommendations
if st.button("🚀 Get Recommendations"):
    with st.spinner("⏳ Analyzing data... Please wait..."):
        time.sleep(2)
        water_needed = calculate_water_requirement(soil, crop, weather, moisture_level)
        harvest_date = calculate_harvest_date(crop, planting_date.strftime("%Y-%m-%d"))
        gpt_prompt = (f"I am growing {crop} in {soil} soil. The weather is {weather} and the soil moisture is {moisture_level}%. "
                      f"How should I manage irrigation and fertilizer?")
        gpt_response = chat_with_gemini(gpt_prompt)
    
    st.markdown(f"""
        <div class="info-box">
            <h3>💧 Recommended Water per day:</h3>
            <p><strong>{water_needed} mm</strong></p>
        </div>
        <div class="info-box">
            <h3>📅 Estimated Harvest Date:</h3>
            <p><strong>{harvest_date}</strong></p>
        </div>
        <div class="info-box">
            <h3>💬 AI Advice:</h3>
            <p>{gpt_response}</p>
        </div>
    """, unsafe_allow_html=True)

# AI Chat Interaction
st.markdown("## 💬 Ask doubts about your crops")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Type your question here...")
if user_input:
    response = chat_with_gemini(user_input)
    st.session_state.chat_history.append(("👨‍🌾 You", user_input))
    st.session_state.chat_history.append(("🤖 AI", response))

for sender, message in st.session_state.chat_history:
    st.chat_message(sender).write(message)