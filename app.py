import streamlit as st
import pandas as pd
import joblib
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Load your trained model and scaler
model = joblib.load("flood_model.pkl")
scaler = joblib.load("scaler.pkl")

# Set page title
st.title("🌊 Flood Prediction App")
st.markdown("Enter environmental and location features to predict flood occurrence.")

# User inputs (must match training column order)
latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, step=0.01)
longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, step=0.01)
rainfall = st.number_input("Rainfall (mm)", min_value=0.0, step=1.0)
temperature = st.number_input("Temperature (°C)", min_value=-50.0, max_value=60.0, step=0.1)
humidity = st.slider("Humidity (%)", 0, 100, 50)
discharge = st.number_input("River Discharge (m³/s)", min_value=0.0, step=10.0)
water_level = st.number_input("Water Level (m)", min_value=0.0, step=0.1)
elevation = st.number_input("Elevation (m)", min_value=0.0, step=1.0)
population_density = st.number_input("Population Density", min_value=0, step=100)
infrastructure = st.selectbox("Infrastructure (Urban=1, Rural=0)", [1, 0])

# Land Cover (One-hot encoding)
land_cover_options = ["Land Cover_0", "Land Cover_1", "Land Cover_2", "Land Cover_3", "Land Cover_4"]
selected_land_cover = st.selectbox("Land Cover Type", land_cover_options)
land_cover_vector = [1 if lc == selected_land_cover else 0 for lc in land_cover_options]

# Soil Type (One-hot encoding)
soil_type_options = ["Soil Type_0", "Soil Type_1", "Soil Type_2", "Soil Type_3", "Soil Type_4"]
selected_soil_type = st.selectbox("Soil Type", soil_type_options)
soil_type_vector = [1 if stype == selected_soil_type else 0 for stype in soil_type_options]

# Create the full input list in correct order
columns_used = [
    'Latitude', 'Longitude', 'Rainfall (mm)', 'Temperature (°C)', 'Humidity (%)', 'River Discharge (m³/s)',
    'Water Level (m)', 'Elevation (m)', 'Population Density', 'Infrastructure',
    'Land Cover_0', 'Land Cover_1', 'Land Cover_2', 'Land Cover_3', 'Land Cover_4',
    'Soil Type_0', 'Soil Type_1', 'Soil Type_2', 'Soil Type_3', 'Soil Type_4'
]

input_data = [
    latitude, longitude, rainfall, temperature, humidity, discharge,
    water_level, elevation, population_density, infrastructure
] + land_cover_vector + soil_type_vector

df_input = pd.DataFrame([input_data], columns=columns_used)

# Prediction
if st.button("Predict Flood Occurrence"):
    scaled_input = scaler.transform(df_input)
    prediction = model.predict(scaled_input)[0]
    st.success(f"Flood Prediction: {'🌊 Flood Likely' if prediction == 1 else '✅ No Flood'}")

# Optional Map (based on dataset)
st.title("🌧️ High Rainfall but No Flood Map")
st.markdown("This map shows **locations with rainfall > 200 mm but no flood occurred**.")

try:
    df = pd.read_csv("flood_risk_dataset_india.csv")

    # Filter locations
    filtered = df[(df['Rainfall (mm)'] > 200) & (df['Flood Occurred'] == 0)]

    if filtered.empty:
        st.warning("No such locations found in the dataset!")
    else:
        map_center = [filtered["Latitude"].mean(), filtered["Longitude"].mean()]
        my_map = folium.Map(location=map_center, zoom_start=5)
        marker_cluster = MarkerCluster().add_to(my_map)

        for _, row in filtered.iterrows():
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=(f"<b>Rainfall:</b> {row['Rainfall (mm)']} mm<br>"
                       f"<b>Temperature:</b> {row['Temperature (°C)']} °C<br>"
                       f"<b>Water Level:</b> {row['Water Level (m)']} m<br>"
                       f"<b>Humidity:</b> {row['Humidity (%)']}%")
            ).add_to(marker_cluster)

        folium_static(my_map)
except Exception as e:
    st.error(f"Failed to load or process dataset: {e}")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define a simple alert function
# Prediction and alert
def send_email_alert(to_email, subject, body):
    from_email = "jha10022002@gmail.com"
    password = "racczdqfmktvskiv"  # Use App Password, NOT your actual password

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        st.success("📨 Alert email sent successfully!")
    except Exception as e:
        st.error(f"Email alert failed: {e}")



if st.button("Send Notification", key="predict_button"):
    scaled_input = scaler.transform(df_input)
    prediction = model.predict(scaled_input)[0]
    result_msg = '🌊 Flood Likely' if prediction == 1 else '✅ No Flood'
    st.success(f"Flood Prediction: {result_msg}")

    if prediction == 1:
        # Customize the recipient and message
        recipient_email = "ayush.jha2021@vitstudent.ac.in"
        subject = "🚨 Flood Alert: Potential Flood Detected"
        body = (f"A flood is likely at location (Lat: {latitude}, Lon: {longitude}).\n"
                f"Rainfall: {rainfall} mm\nTemperature: {temperature} °C\n"
                f"Humidity: {humidity}%\nWater Level: {water_level} m\n"
                f"Please take necessary precautions.")
        send_email_alert(recipient_email, subject, body)

