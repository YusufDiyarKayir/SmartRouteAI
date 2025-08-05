from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Simple AI Service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analyze-prompt', methods=['POST'])
def analyze_prompt():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    # Basit prompt analizi
    cities = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya', 'Gaziantep']
    found_cities = [city for city in cities if city.lower() in prompt.lower()]
    
    analysis = {
        'source': found_cities[0] if len(found_cities) > 0 else 'Belirlenemedi',
        'destination': found_cities[1] if len(found_cities) > 1 else 'Belirlenemedi',
        'requests': ['hızlı rota'] if 'hızlı' in prompt.lower() else [],
        'bridgeDirectives': [],
        'highwayDirectives': [],
        'weatherConditions': ['yağmur'] if 'yağmur' in prompt.lower() else []
    }
    
    return jsonify(analysis)

@app.route('/plan', methods=['POST'])
def plan_route():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    # Basit rota planlama
    cities = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya', 'Gaziantep']
    found_cities = [city for city in cities if city.lower() in prompt.lower()]
    
    if len(found_cities) < 2:
        return jsonify({'error': 'En az 2 şehir belirtilmelidir'})
    
    # Tatil bilgileri
    holiday_info = {
        'isHoliday': random.choice([True, False]),
        'isWeekend': random.choice([True, False]),
        'dayOfWeek': 'Pazartesi',
        'holidayName': 'Normal gün',
        'trafficMultiplier': random.uniform(0.8, 1.5)
    }
    
    # Alternatif rotalar
    alternatives = []
    for i in range(3):
        route = {
            'title': f'Rota {i+1}',
            'distanceKm': random.randint(200, 800),
            'durationMin': random.randint(120, 480),
            'adjustedDurationMin': random.randint(120, 480),
            'hasToll': random.choice([True, False]),
            'weatherImpact': 'Normal hava koşulları',
            'polyline': 'mock_polyline_data',
            'summary': f'{found_cities[0]} - {found_cities[1]} rota {i+1}'
        }
        alternatives.append(route)
    
    # Hava durumu tahminleri
    weather_predictions = []
    for city in found_cities:
        prediction = {
            'city': city,
            'predictedWeather': random.choice(['güneşli', 'yağmurlu', 'bulutlu']),
            'avgTemperature': random.randint(10, 30),
            'confidence': random.uniform(0.7, 0.95)
        }
        weather_predictions.append(prediction)
    
    result = {
        'alternatives': alternatives,
        'holidayInfo': holiday_info,
        'weatherPredictions': weather_predictions
    }
    
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Simple AI Service başlatılıyor...")
    print("📍 Endpoint: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 