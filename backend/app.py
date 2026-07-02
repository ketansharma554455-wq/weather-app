import joblib
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Cities with coordinates
CITIES = {
    "Dayal Bagh, Agra": {"lat": 27.1788, "lon": 78.0158},
    "Agra City": {"lat": 27.1767, "lon": 78.0081},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639}
}
model = joblib.load("model.pkl")

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Asia/Kolkata"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        current = data['current_weather']
        return current['temperature'], current['windspeed']
    except:
        return None, None

@app.route('/api/weather')
def api_weather():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Prediction Model</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                font-family: 'Inter', sans-serif;
                padding: 20px;
                min-height: 100vh;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            
            /* Glass Card Effect */
            .glass {
                background: rgba(255,255,255,0.08);
                backdrop-filter: blur(12px);
                border-radius: 24px;
                border: 1px solid rgba(255,255,255,0.15);
            }
            
            /* Header */
            .header {
                text-align: center;
                padding: 30px;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5em;
                background: linear-gradient(135deg, #FFD700, #FF6B6B);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: 1px;
            }
            
            /* City Selector */
            .city-selector {
                margin-bottom: 25px;
            }
            select {
                width: 100%;
                padding: 14px 20px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 16px;
                color: white;
                font-size: 1em;
                cursor: pointer;
                backdrop-filter: blur(10px);
            }
            select option { background: #1a1a2e; }
            
            /* Stats Grid - 4 Cards */
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 25px;
            }
            .stat-card {
                background: rgba(255,255,255,0.08);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .stat-card:hover {
                transform: translateY(-5px);
                border-color: #FFD700;
                box-shadow: 0 10px 30px rgba(255,215,0,0.2);
            }
            .stat-icon { font-size: 2.5em; margin-bottom: 10px; }
            .stat-value { font-size: 2em; font-weight: bold; color: #FFD700; margin: 8px 0; }
            .stat-label { color: rgba(255,255,255,0.7); font-size: 0.85em; }
            .stat-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.7em;
                margin-top: 8px;
            }
            .badge-hot { background: rgba(255,107,107,0.2); color: #ff6b6b; }
            .badge-normal { background: rgba(78,205,196,0.2); color: #4ecdc4; }
            .badge-cold { background: rgba(78,205,196,0.2); color: #4ecdc4; }
            
            /* AI Prediction Box */
            .prediction-box {
                background: linear-gradient(135deg, rgba(240,147,251,0.2), rgba(245,87,108,0.2));
                backdrop-filter: blur(10px);
                border-radius: 24px;
                padding: 25px;
                text-align: center;
                margin-bottom: 25px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .prediction-value {
                font-size: 3.5em;
                font-weight: bold;
                color: #FFD700;
                text-shadow: 0 0 20px rgba(255,215,0,0.3);
                margin: 10px 0;
            }
            
            /* Alert Row */
            .alert-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 25px;
            }
            .alert-card {
                background: rgba(255,255,255,0.08);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 18px;
                border-left: 4px solid;
                transition: all 0.3s;
            }
            .alert-card:hover { transform: translateY(-3px); }
            .rain-alert { border-left-color: #4ecdc4; }
            .storm-alert { border-left-color: #ff6b6b; }
            
            /* Forecast */
            .forecast-section {
                background: rgba(255,255,255,0.08);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 25px;
            }
            .forecast-title { color: #FFD700; margin-bottom: 15px; font-size: 1.1em; }
            .forecast-grid {
                display: grid;
                grid-template-columns: repeat(12, 1fr);
                gap: 10px;
                overflow-x: auto;
            }
            .forecast-hour {
                text-align: center;
                padding: 10px;
                background: rgba(0,0,0,0.3);
                border-radius: 12px;
                min-width: 70px;
            }
            .forecast-temp { font-weight: bold; margin-top: 5px; color: #FFD700; }
            
            /* Status Bar */
            .status-bar {
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                margin-top: 20px;
            }
            .led {
                width: 10px;
                height: 10px;
                background: #00ff00;
                border-radius: 50%;
                animation: blink 1s infinite;
                display: inline-block;
                margin-right: 8px;
            }
            @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
            
            @media (max-width: 768px) {
                .stats-grid { grid-template-columns: repeat(2, 1fr); }
                .alert-row { grid-template-columns: 1fr; }
                .forecast-grid { grid-template-columns: repeat(6, 1fr); }
                .header h1 { font-size: 1.5em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header glass">
                <h1>🌤️ WEATHER PREDICTION MODEL</h1>
            </div>
            
            <div class="city-selector">
                <select id="citySelect">
                    <option value="27.1788,78.0158">📍 Dayal Bagh, Agra</option>
                    <option value="27.1767,78.0081">📍 Agra City</option>
                    <option value="28.6139,77.2090">📍 Delhi</option>
                    <option value="19.0760,72.8777">📍 Mumbai</option>
                    <option value="26.9124,75.7873">📍 Jaipur</option>
                    <option value="26.8467,80.9462">📍 Lucknow</option>
                    <option value="13.0827,80.2707">📍 Chennai</option>
                    <option value="12.9716,77.5946">📍 Bangalore</option>
                    <option value="22.5726,88.3639">📍 Kolkata</option>
                </select>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">🌡️</div>
                    <div class="stat-value" id="temp">--°C</div>
                    <div class="stat-label">Temperature</div>
                    <div class="stat-badge" id="tempBadge">---</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💧</div>
                    <div class="stat-value" id="humidity">--%</div>
                    <div class="stat-label">Humidity</div>
                    <div class="stat-badge" id="humidityBadge">---</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💨</div>
                    <div class="stat-value" id="wind">-- km/h</div>
                    <div class="stat-label">Wind Speed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-value" id="pressure">-- hPa</div>
                    <div class="stat-label">Pressure</div>
                </div>
            </div>
            
            <div class="prediction-box">
                <div>🤖 AI PREDICTION</div>
                <div class="prediction-value" id="prediction">--°C</div>
                <div>Next Hour Forecast</div>
            </div>
            
            <div class="alert-row">
                <div class="alert-card rain-alert">
                    <div>🌧️ RAIN ALERT</div>
                    <div>Chance: <span id="rainChance">--</span>%</div>
                    <div>Time: <span id="rainTime">--</span></div>
                </div>
                <div class="alert-card storm-alert">
                    <div>🌪️ STORM ALERT</div>
                    <div>Chance: <span id="stormChance">--</span>%</div>
                    <div>Wind: <span id="stormWind">--</span> km/h</div>
                </div>
            </div>
            
            <div class="forecast-section">
                <div class="forecast-title">📅 24 HOUR FORECAST</div>
                <div class="forecast-grid" id="forecast"></div>
            </div>
            
            <div class="status-bar">
                <div><span class="led"></span> LIVE</div>
                <div>🔄 Last Update: <span id="updateTime">--</span></div>
                <div>📡 Open-Meteo</div>
            </div>
        </div>
        
        <script>
            async function fetchData() {
                const citySelect = document.getElementById('citySelect');
                const coords = citySelect.value.split(',');
                const lat = coords[0];
                const lon = coords[1];
                
                try {
                    const res = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
                    const data = await res.json();
                    
                    document.getElementById('temp').innerHTML = data.temp + '°C';
                    document.getElementById('humidity').innerHTML = data.humidity + '%';
                    document.getElementById('wind').innerHTML = data.wind + ' km/h';
                    document.getElementById('pressure').innerHTML = data.pressure + ' hPa';
                    document.getElementById('prediction').innerHTML = data.prediction + '°C';
                    document.getElementById('rainChance').innerHTML = data.rainChance;
                    document.getElementById('rainTime').innerHTML = data.rainTime;
                    document.getElementById('stormChance').innerHTML = data.stormChance;
                    document.getElementById('stormWind').innerHTML = data.stormWind;
                    document.getElementById('updateTime').innerHTML = new Date().toLocaleTimeString();
                    
                    // Temp Badge
                    let tempBadge = document.getElementById('tempBadge');
                    if(data.temp > 35) tempBadge.innerHTML = '🔥 EXTREME';
                    else if(data.temp > 30) tempBadge.innerHTML = '⚠️ HOT';
                    else if(data.temp < 15) tempBadge.innerHTML = '❄️ COLD';
                    else tempBadge.innerHTML = '✅ NORMAL';
                    
                    // Humidity Badge
                    let humidityBadge = document.getElementById('humidityBadge');
                    if(data.humidity > 80) humidityBadge.innerHTML = '💧 HIGH';
                    else if(data.humidity < 30) humidityBadge.innerHTML = '🏜️ LOW';
                    else humidityBadge.innerHTML = '✅ NORMAL';
                    
                    // Forecast
                    let forecastHtml = '';
                    for(let i = 0; i < data.forecast.length; i++) {
                        forecastHtml += `
                            <div class="forecast-hour">
                                ${data.forecast[i].time}<br>
                                <span class="forecast-temp">${data.forecast[i].temp}°</span>
                            </div>
                        `;
                    }
                    document.getElementById('forecast').innerHTML = forecastHtml;
                    
                } catch(e) {
                    console.error('Error:', e);
                }
            }
            
            document.getElementById('citySelect').onchange = fetchData;
            fetchData();
            setInterval(fetchData, 30000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/weather')
def api_weather():
    lat = request.args.get('lat', '27.1788')
    lon = request.args.get('lon', '78.0158')
    
    temp, wind = get_weather(float(lat), float(lon))
    
    if temp is None:
        temp = round(random.uniform(25, 35), 1)
        wind = round(random.uniform(5, 15), 1)
    
    humidity = random.randint(40, 70)
    pressure = random.randint(1005, 1015)
    
    # Storm calculation
    stormChance = 0
    if wind > 25:
        stormChance = random.randint(40, 70)
    elif wind > 18:
        stormChance = random.randint(15, 35)
    
    # Rain calculation
    rainChance = random.randint(10, 45)
    if rainChance > 30:
        rainTime = "8:00 PM - 10:00 PM"
    elif rainChance > 15:
        rainTime = "10:00 PM - 12:00 AM"
    else:
        rainTime = "No rain expected"
    
    # AI Prediction
  # AI MODEL PREDICTION

now = datetime.now()

features = [[
    now.hour,
    now.day,
    now.month,
    now.weekday(),
    humidity,
    wind,
    pressure
]]

pred = model.predict(features)[0]
pred = round(float(pred), 1)
forecast = []

for i in range(1, 13):

    future = now + timedelta(hours=i)

    future_features = [[
        future.hour,
        future.day,
        future.month,
        future.weekday(),
        humidity,
        wind,
        pressure
    ]]

    future_temp = model.predict(future_features)[0]

    forecast.append({
        'time': future.strftime('%I:%M %p'),
        'temp': round(float(future_temp), 1)
    })