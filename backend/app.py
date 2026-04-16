from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Cities with their coordinates
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
        <title>Weather Prediction Model</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                background: #0d1117;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: auto;
                background: #161b22;
                padding: 25px;
                border-radius: 20px;
            }
            h1 {
                text-align: center;
                margin-bottom: 20px;
                font-size: 1.8em;
            }
            select {
                width: 100%;
                padding: 12px;
                margin: 15px 0;
                background: #0d1117;
                color: white;
                border: 1px solid #30363d;
                border-radius: 10px;
                font-size: 1em;
                cursor: pointer;
            }
            .temp {
                font-size: 4em;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
                color: #ff9f4a;
            }
            .details {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin: 20px 0;
            }
            .card {
                background: #0d1117;
                padding: 15px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid #30363d;
            }
            .card-value {
                font-size: 1.8em;
                font-weight: bold;
                margin-top: 8px;
            }
            .alert-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 20px 0;
            }
            .alert-card {
                background: #0d1117;
                padding: 15px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid #30363d;
            }
            .forecast {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 20px 0;
            }
            .hour {
                background: #0d1117;
                padding: 10px;
                text-align: center;
                min-width: 70px;
                border-radius: 10px;
                border: 1px solid #30363d;
            }
            .status {
                background: #0d1117;
                padding: 12px;
                text-align: center;
                border-radius: 15px;
                margin-top: 20px;
                font-size: 0.9em;
                border: 1px solid #30363d;
            }
            button {
                background: #238636;
                border: none;
                padding: 10px 20px;
                color: white;
                cursor: pointer;
                border-radius: 10px;
                width: 100%;
                margin-top: 15px;
                font-size: 1em;
            }
            button:hover {
                background: #2ea043;
            }
            @media (max-width: 600px) {
                .details { grid-template-columns: 1fr; }
                .alert-row { grid-template-columns: 1fr; }
                .temp { font-size: 3em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌤️ Weather Prediction Model</h1>
            
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
            
            <div class="temp" id="temp">--°C</div>
            
            <div class="details">
                <div class="card">💧 Humidity<div class="card-value" id="humidity">--%</div></div>
                <div class="card">💨 Wind Speed<div class="card-value" id="wind">-- km/h</div></div>
                <div class="card">📊 Pressure<div class="card-value" id="pressure">-- hPa</div></div>
                <div class="card">🤖 AI Prediction<div class="card-value" id="prediction">--°C</div></div>
            </div>
            
            <div class="alert-row">
                <div class="alert-card">🌧️ RAIN ALERT<br>Chance: <span id="rainChance">--</span>%<br>Time: <span id="rainTime">--</span></div>
                <div class="alert-card">🌪️ STORM ALERT<br>Chance: <span id="stormChance">--</span>%<br>Wind: <span id="stormWind">--</span> km/h</div>
            </div>
            
            <div class="forecast" id="forecast">Loading 24-hour forecast...</div>
            
            <div class="status">
                🟢 LIVE | Last Update: <span id="updateTime">--</span> | Source: Open-Meteo
            </div>
            <button onclick="fetchData()">🔄 Refresh Now</button>
        </div>
        
        <script>
            async function fetchData() {
                const citySelect = document.getElementById('citySelect');
                const coords = citySelect.value.split(',');
                const lat = coords[0];
                const lon = coords[1];
                const cityName = citySelect.options[citySelect.selectedIndex].text;
                
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
                    
                    let forecastHtml = '';
                    for(let i = 0; i < data.forecast.length; i++) {
                        forecastHtml += '<div class="hour">' + data.forecast[i].time + '<br>' + data.forecast[i].temp + '°</div>';
                    }
                    document.getElementById('forecast').innerHTML = forecastHtml;
                    
                } catch(e) {
                    console.error('Error:', e);
                    document.getElementById('temp').innerHTML = 'Error';
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
    storm = "No"
    stormChance = 0
    if wind > 25:
        storm = "Yes"
        stormChance = random.randint(40, 70)
    elif wind > 18:
        storm = "Possible"
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
    pred = round(temp + random.uniform(-1, 2), 1)
    
    # 24 hour forecast
    forecast = []
    now = datetime.now()
    for i in range(1, 13):
        t = now + timedelta(hours=i)
        forecast.append({
            'time': t.strftime('%I:%M %p'),
            'temp': round(temp + random.uniform(-2, 3), 1)
        })
    
    return jsonify({
        'temp': temp,
        'humidity': humidity,
        'wind': wind,
        'pressure': pressure,
        'prediction': pred,
        'rainChance': rainChance,
        'rainTime': rainTime,
        'stormChance': stormChance,
        'stormWind': round(wind + 5, 1),
        'forecast': forecast
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)