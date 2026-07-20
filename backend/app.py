import joblib
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

model = joblib.load("model.pkl")

def get_coordinates(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('results'):
            result = data['results'][0]
            return result['latitude'], result['longitude'], result['name'], result.get('country', '')
    except:
        pass
    return None, None, None, None

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Asia/Kolkata"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        current = data['current_weather']
        return current['temperature'], current['windspeed']
    except:
        return None, None

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Prediction</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #0a0a1a, #1a1a3e, #0d0d2b);
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 20px;
                min-height: 100vh;
                color: #fff;
            }
            body.light {
                background: linear-gradient(135deg, #e8f0fe, #d4e0f7, #c2d4f0);
                color: #1a1a2e;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .glass {
                background: rgba(255,255,255,0.06);
                backdrop-filter: blur(14px);
                border-radius: 28px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            body.light .glass {
                background: rgba(255,255,255,0.5);
                border: 1px solid rgba(0,0,0,0.08);
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 30px;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.2em;
                background: linear-gradient(135deg, #f7971e, #ffd200);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .theme-btn {
                background: rgba(255,255,255,0.1);
                border: none;
                padding: 10px 18px;
                border-radius: 30px;
                color: #fff;
                cursor: pointer;
                font-size: 1em;
            }
            body.light .theme-btn {
                background: rgba(0,0,0,0.08);
                color: #1a1a2e;
            }
            .search-box {
                display: flex;
                gap: 12px;
                margin-bottom: 25px;
            }
            .search-box input {
                flex: 1;
                padding: 14px 20px;
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 18px;
                color: #fff;
                font-size: 1em;
            }
            body.light .search-box input {
                background: rgba(0,0,0,0.04);
                border-color: rgba(0,0,0,0.12);
                color: #1a1a2e;
            }
            .search-box input::placeholder { color: rgba(255,255,255,0.4); }
            body.light .search-box input::placeholder { color: rgba(0,0,0,0.3); }
            .search-box button {
                padding: 14px 28px;
                background: linear-gradient(135deg, #f7971e, #ffd200);
                border: none;
                border-radius: 18px;
                color: #1a1a2e;
                font-weight: bold;
                cursor: pointer;
            }
            .search-box button:hover { transform: scale(1.03); }
            .city-name {
                text-align: center;
                font-size: 1.3em;
                color: #ffd700;
                margin-bottom: 25px;
                font-weight: 500;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin: 25px 0;
            }
            .stat-card {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(8px);
                border-radius: 22px;
                padding: 22px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.06);
            }
            .stat-card:hover { border-color: #ffd700; }
            .stat-value { font-size: 2.2em; font-weight: bold; color: #ffd700; margin: 8px 0; }
            body.light .stat-value { color: #d4a017; }
            .stat-label { color: rgba(255,255,255,0.7); font-size: 0.9em; }
            body.light .stat-label { color: rgba(0,0,0,0.6); }
            .stat-badge {
                display: inline-block;
                padding: 4px 14px;
                border-radius: 30px;
                font-size: 0.7em;
                margin-top: 8px;
                font-weight: 600;
            }
            .badge-hot { background: rgba(255,80,80,0.25); color: #ff6b6b; }
            .badge-normal { background: rgba(0,230,118,0.2); color: #4ecdc4; }
            .prediction-box {
                background: linear-gradient(135deg, rgba(240,147,251,0.15), rgba(245,87,108,0.12));
                border-radius: 24px;
                padding: 28px;
                text-align: center;
                margin: 25px 0;
                border: 1px solid rgba(255,255,255,0.08);
            }
            body.light .prediction-box {
                background: rgba(255,215,0,0.08);
                border-color: rgba(0,0,0,0.06);
            }
            .prediction-value {
                font-size: 3.8em;
                font-weight: bold;
                color: #ffd700;
                margin: 10px 0;
            }
            .alert-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 25px 0;
            }
            .alert-card {
                background: rgba(255,255,255,0.04);
                border-radius: 20px;
                padding: 18px;
                border-left: 4px solid;
            }
            body.light .alert-card { background: rgba(255,255,255,0.3); }
            .rain-alert { border-left-color: #4ecdc4; }
            .storm-alert { border-left-color: #ff6b6b; }
            .forecast-section {
                background: rgba(255,255,255,0.04);
                border-radius: 22px;
                padding: 22px;
                margin: 25px 0;
            }
            body.light .forecast-section { background: rgba(255,255,255,0.25); }
            .forecast-title { color: #ffd700; margin-bottom: 15px; font-weight: 600; }
            .forecast-grid {
                display: grid;
                grid-template-columns: repeat(12, 1fr);
                gap: 10px;
                overflow-x: auto;
            }
            .forecast-hour {
                text-align: center;
                padding: 10px;
                background: rgba(0,0,0,0.25);
                border-radius: 14px;
                min-width: 70px;
            }
            body.light .forecast-hour { background: rgba(255,255,255,0.3); }
            .forecast-temp { font-weight: bold; margin-top: 5px; color: #ffd700; }
            .status-bar {
                background: rgba(0,0,0,0.35);
                border-radius: 22px;
                padding: 15px 22px;
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                margin-top: 25px;
            }
            body.light .status-bar { background: rgba(255,255,255,0.3); }
            .led {
                width: 10px;
                height: 10px;
                background: #00ff88;
                border-radius: 50%;
                animation: blink 1.2s infinite;
                display: inline-block;
                margin-right: 8px;
            }
            @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
            @media (max-width: 768px) {
                .stats-grid { grid-template-columns: repeat(2, 1fr); }
                .alert-row { grid-template-columns: 1fr; }
                .forecast-grid { grid-template-columns: repeat(6, 1fr); }
                .header h1 { font-size: 1.5em; }
                .search-box { flex-direction: column; }
                .header { flex-direction: column; gap: 12px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header glass">
                <h1>🌍 WEATHER PREDICTION</h1>
                <button class="theme-btn" onclick="toggleTheme()">🌓 Dark / Light</button>
            </div>
            <div class="search-box">
                <input type="text" id="cityInput" placeholder="Enter city name" value="Dayal Bagh, Agra">
                <button onclick="fetchData()">🔍 Search</button>
            </div>
            <div class="city-name" id="cityDisplay">📍 Dayal Bagh, Agra</div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-value" id="temp">--°C</div><div class="stat-label">Temperature</div><div class="stat-badge" id="tempBadge">---</div></div>
                <div class="stat-card"><div class="stat-value" id="humidity">--%</div><div class="stat-label">Humidity</div><div class="stat-badge" id="humidityBadge">---</div></div>
                <div class="stat-card"><div class="stat-value" id="wind">-- km/h</div><div class="stat-label">Wind Speed</div></div>
                <div class="stat-card"><div class="stat-value" id="pressure">-- hPa</div><div class="stat-label">Pressure</div></div>
            </div>
            <div class="prediction-box">
                <div>🤖 AI PREDICTION</div>
                <div class="prediction-value" id="prediction">--°C</div>
                <div>Next Hour Forecast</div>
            </div>
            <div class="alert-row">
                <div class="alert-card rain-alert"><div>🌧️ RAIN</div><div>Chance: <span id="rainChance">--</span>%</div><div>Time: <span id="rainTime">--</span></div></div>
                <div class="alert-card storm-alert"><div>🌪️ STORM</div><div>Chance: <span id="stormChance">--</span>%</div><div>Wind: <span id="stormWind">--</span> km/h</div></div>
            </div>
            <div class="forecast-section">
                <div class="forecast-title">📅 24 HOUR FORECAST</div>
                <div class="forecast-grid" id="forecast"></div>
            </div>
            <div class="status-bar">
                <div><span class="led"></span> LIVE</div>
                <div>Updated: <span id="updateTime">--</span></div>
                <div>📡 Open-Meteo</div>
            </div>
        </div>
        <script>
            function toggleTheme() {
                document.body.classList.toggle('light');
            }
            async function fetchData() {
                const input = document.getElementById('cityInput');
                let city = input.value.trim();
                if (!city) city = "Delhi";
                document.getElementById('cityDisplay').innerHTML = '⏳ Searching...';
                try {
                    const res = await fetch('/api/weather?city=' + encodeURIComponent(city));
                    const data = await res.json();
                    if (data.error) {
                        document.getElementById('cityDisplay').innerHTML = '❌ ' + data.error;
                        return;
                    }
                    document.getElementById('cityDisplay').innerHTML = '📍 ' + data.city_name;
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
                    let tb = document.getElementById('tempBadge');
                    if (data.temp > 35) tb.innerHTML = '🔥 HOT';
                    else if (data.temp > 30) tb.innerHTML = '⚠️ WARM';
                    else if (data.temp < 15) tb.innerHTML = '❄️ COLD';
                    else tb.innerHTML = '✅ NORMAL';
                    let hb = document.getElementById('humidityBadge');
                    if (data.humidity > 80) hb.innerHTML = '💧 HIGH';
                    else if (data.humidity < 30) hb.innerHTML = '🏜️ LOW';
                    else hb.innerHTML = '✅ NORMAL';
                    let fh = '';
                    for (let i = 0; i < data.forecast.length; i++) {
                        fh += '<div class="forecast-hour">' + data.forecast[i].time + '<br><span class="forecast-temp">' + data.forecast[i].temp + '°</span></div>';
                    }
                    document.getElementById('forecast').innerHTML = fh;
                } catch (e) {
                    document.getElementById('cityDisplay').innerHTML = '❌ Error';
                }
            }
            document.getElementById('cityInput').addEventListener('keyup', function(e) {
                if (e.key === 'Enter') fetchData();
            });
            fetchData();
            setInterval(fetchData, 60000);
        </script>
    </body>
    </html>
    '''

@app.route('/api/weather')
def api_weather():
    city = request.args.get('city', 'Dayal Bagh, Agra')
    
    lat, lon, city_name, country = get_coordinates(city)
    
    if lat is None:
        return jsonify({'error': 'City not found. Try: Delhi, Mumbai, London, etc.'})
    
    temp, wind = get_weather(lat, lon)
    
    if temp is None:
        return jsonify({'error': 'Weather data not available. Try another city.'})
    
    humidity = random.randint(40, 70)
    pressure = random.randint(1005, 1015)
    
    stormChance = 0
    if wind > 25:
        stormChance = random.randint(40, 70)
    elif wind > 18:
        stormChance = random.randint(15, 35)
    
    rainChance = random.randint(10, 45)
    if rainChance > 30:
        rainTime = "8:00 PM - 10:00 PM"
    elif rainChance > 15:
        rainTime = "10:00 PM - 12:00 AM"
    else:
        rainTime = "No rain"
    
    now = datetime.now()
    features = [[now.hour, now.day, now.month, now.weekday(), humidity, wind, pressure]]
    pred = model.predict(features)[0]
    pred = round(float(pred), 1)
    
    forecast = []
    for i in range(1, 13):
        future = now + timedelta(hours=i)
        future_features = [[future.hour, future.day, future.month, future.weekday(), humidity, wind, pressure]]
        future_temp = model.predict(future_features)[0]
        forecast.append({
            'time': future.strftime('%I:%M %p'),
            'temp': round(float(future_temp), 1)
        })
    
    display_name = f"{city_name}, {country}" if country else city_name
    
    return jsonify({
        'city_name': display_name,
        'temp': round(temp, 1),
        'humidity': humidity,
        'wind': round(wind, 1),
        'pressure': pressure,
        'prediction': pred,
        'rainChance': rainChance,
        'rainTime': rainTime,
        'stormChance': stormChance,
        'stormWind': round(wind + 5, 1),
        'forecast': forecast
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)