import streamlit as st
import requests
import json

# Try importing streamlit_js_eval (only works locally)
try:
    from streamlit_js_eval import get_geolocation
    GEO_ENABLED = True
except ModuleNotFoundError:
    GEO_ENABLED = False

from google import genai

# -------------------------------
# APP CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="🌦️ Smart Weather App",
    page_icon="🌤️",
    layout="wide"
)

# -------------------------------
# API KEYS
# -------------------------------
WEATHER_API_KEY = "bf89bc2cde67abeceea98d4c23a10716"
GEMINI_API_KEY = "AIzaSyAttkG_z68w3a0vPD3VjHSv7543iefWPtc"

client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------------
# APP HEADER
# -------------------------------
st.title("🌦️ Smart Weather App")
st.markdown("""
Get **live weather updates** and **AI-powered suggestions**  
for health, clothing, and lifestyle — all based on your location 🌍.
""")

st.divider()

# -------------------------------
# STEP 1: Location Detection
# -------------------------------
st.subheader("📍 Location Detection")

if GEO_ENABLED:
    if "location_data" not in st.session_state:
        st.session_state.location_data = None

    if st.button("🔄 Refresh Location"):
        st.session_state.location_data = None

    if st.session_state.location_data is None:
        with st.spinner("🗺️ Detecting your location... please allow browser access."):
            loc = get_geolocation()
            if loc:
                st.session_state.location_data = loc
            else:
                st.warning("⚠️ Please click 'Allow' when your browser asks for location access.")
                st.stop()

    loc = st.session_state.location_data
    lat = loc["coords"]["latitude"]
    lon = loc["coords"]["longitude"]
    st.success(f"✅ Location detected successfully! **Latitude:** `{lat:.4f}` | **Longitude:** `{lon:.4f}`")

else:
    st.warning("⚠️ Automatic location not supported on Streamlit Cloud. Enter your city manually.")
    city = st.text_input("Enter your city 🌍", "Hyderabad")

    if not city:
        st.stop()

    # Fetch coordinates by city
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(weather_url)
    if res.status_code != 200:
        st.error("❌ Unable to fetch weather data. Please check your city name.")
        st.stop()

    data_we = res.json()
    lat = data_we["coord"]["lat"]
    lon = data_we["coord"]["lon"]

# -------------------------------
# STEP 2: Fetch Weather Data
# -------------------------------
if GEO_ENABLED:
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(weather_url)
    data_we = res.json()

city = data_we.get("name", "Unknown Location")
weather_desc = data_we["weather"][0]["description"].title()
temp = data_we["main"]["temp"]
humidity = data_we["main"]["humidity"]
wind_speed = data_we["main"]["speed"] if "speed" in data_we["main"] else data_we["wind"]["speed"]
icon = data_we["weather"][0]["icon"]
icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"

# -------------------------------
# STEP 3: Display Weather Info
# -------------------------------
col_map, col_weather = st.columns([1.2, 1.3])

with col_map:
    st.subheader("🗺️ Your Location on Map")
    st.map([{"lat": lat, "lon": lon}])

with col_weather:
    st.subheader(f"🌤️ Weather in {city}")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(icon_url, width=90)
    with c2:
        st.markdown(f"**Condition:** {weather_desc}")
        st.metric("🌡️ Temperature", f"{temp}°C")
        st.metric("💧 Humidity", f"{humidity}%")
        st.metric("🌬️ Wind Speed", f"{wind_speed} m/s")

st.divider()

# -------------------------------
# STEP 4: Gemini AI Recommendations
# -------------------------------
st.subheader("🤖 AI Weather Advice")

weather_json = json.dumps(data_we, indent=2)

with st.spinner("💭 Analyzing your weather... please wait"):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""
        You are a helpful AI weather assistant.
        Here is the current weather JSON:
        {weather_json}

        Based on this data, provide:
        1. 🩺 Health precautions
        2. 👕 Clothing suggestions
        3. 🍴 Food recommendations
        4. 🌈 Lifestyle or travel tips

        Return the output as short, clear bullet points.
        """
    )

st.success("✅ AI Suggestions Ready!")
st.markdown(response.text)

st.divider()
st.caption("Built with 💙 Streamlit + Gemini AI | Smart Weather App © 2025")
