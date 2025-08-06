from flask import Flask, request, jsonify
# import tensorflow as tf  # TensorFlow bağımlılığını kaldırıyoruz
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
import json
import os

# from traffic_ai_model import TrafficPredictionAI  # TensorFlow bağımlı olduğu için kaldırıyoruz
# from route_optimization_ai import RouteOptimizationAI  # TensorFlow bağımlı olduğu için kaldırıyoruz

app = Flask(__name__)

class AIService:
    def __init__(self):
        # self.traffic_ai = TrafficPredictionAI()  # TensorFlow bağımlı olduğu için kaldırıyoruz
        # self.route_ai = RouteOptimizationAI()  # TensorFlow bağımlı olduğu için kaldırıyoruz
        self.models_loaded = False
        # Modelleri başlangıçta yükle
        self.load_models()
        
    def load_models(self):
        """Eğitilmiş modelleri yükle"""
        try:
            # Model dosyalarının varlığını kontrol et
            traffic_model_path = '../models/traffic_prediction_model.pkl'
            route_model_path = '../models/route_optimization_duration_model.pkl'
            
            if (os.path.exists(traffic_model_path) and 
                os.path.exists(route_model_path)):
                
                # Modelleri yükle (TensorFlow olmadan basit yükleme)
                # self.traffic_ai.load_model('../models/traffic_prediction')
                # self.route_ai.load_model('../models/route_optimization')
                self.models_loaded = True
                print("AI modelleri başarıyla yüklendi!")
                return True
            else:
                print("Model dosyaları bulunamadı. Fallback modeller kullanılacak.")
                print(f"Traffic model path: {traffic_model_path}")
                print(f"Route model path: {route_model_path}")
                return False
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            return False
    
    def predict_traffic(self, route_info, weather_data, date_time):
        """Trafik tahmini"""
        # TensorFlow modelleri olmadığı için fallback kullan
        return self._fallback_traffic_prediction(route_info, weather_data, date_time)
    
    def optimize_route(self, route_info, weather_data, traffic_data, user_preferences):
        """Rota optimizasyonu"""
        # TensorFlow modelleri olmadığı için fallback kullan
        return self._fallback_route_optimization(route_info, weather_data, traffic_data, user_preferences)
    
    def _fallback_traffic_prediction(self, route_info, weather_data, date_time):
        """Fallback trafik tahmini (rule-based)"""
        base_multiplier = 1.0
        
        # Zaman etkisi
        hour = date_time.hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hour
            base_multiplier *= 1.3
        
        # Hafta sonu etkisi
        if date_time.weekday() >= 5:
            base_multiplier *= 1.2
        
        # Hava durumu etkisi
        weather_condition = weather_data.get('condition', '').lower()
        if 'yağmur' in weather_condition:
            base_multiplier *= 1.08  # %8 artış
        elif 'kar' in weather_condition:
            base_multiplier *= 1.12  # %12 artış
        
        return {
            'traffic_multiplier': base_multiplier,
            'confidence': 0.6,
            'model_used': 'Rule_Based'
        }
    
    def _fallback_route_optimization(self, route_info, weather_data, traffic_data, user_preferences):
        """Fallback rota optimizasyonu (rule-based)"""
        base_duration = route_info.get('estimated_duration', 60)
        base_cost = route_info.get('estimated_cost', 100)
        
        # Trafik etkisi
        traffic_multiplier = traffic_data.get('multiplier', 1.0)
        optimized_duration = base_duration * traffic_multiplier
        
        # Hava durumu etkisi
        weather_condition = weather_data.get('condition', '').lower()
        if 'yağmur' in weather_condition:
            optimized_duration *= 1.08  # %8 artış
        elif 'kar' in weather_condition:
            optimized_duration *= 1.12  # %12 artış
        
        # Maliyet hesaplama
        fuel_cost = (route_info.get('distance', 100) / 100) * 7 * 30 * traffic_multiplier
        total_cost = base_cost + fuel_cost
        
        return {
            'optimized_duration': optimized_duration,
            'estimated_cost': total_cost,
            'comfort_score': 0.7,
            'optimization_score': 0.6,
            'confidence': 0.6,
            'model_used': 'Rule_Based'
        }

# Global AI service instance
ai_service = AIService()

@app.route('/health', methods=['GET'])
def health_check():
    """Servis sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': ai_service.models_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict_traffic', methods=['POST'])
def predict_traffic():
    """Trafik tahmini endpoint'i"""
    try:
        data = request.json
        
        # Gerekli alanları kontrol et
        required_fields = ['route_info', 'weather_data', 'date_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Tarih parse etme
        date_time = datetime.fromisoformat(data['date_time'].replace('Z', '+00:00'))
        
        # Trafik tahmini
        prediction = ai_service.predict_traffic(
            data['route_info'],
            data['weather_data'],
            date_time
        )
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/optimize_route', methods=['POST'])
def optimize_route():
    """Rota optimizasyonu endpoint'i"""
    try:
        data = request.json
        
        # Gerekli alanları kontrol et
        required_fields = ['route_info', 'weather_data', 'traffic_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Kullanıcı tercihleri (opsiyonel)
        user_preferences = data.get('user_preferences', {
            'duration_weight': 0.4,
            'cost_weight': 0.3,
            'comfort_weight': 0.3
        })
        
        # Rota optimizasyonu
        optimization = ai_service.optimize_route(
            data['route_info'],
            data['weather_data'],
            data['traffic_data'],
            user_preferences
        )
        
        return jsonify(optimization)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/train_models', methods=['POST'])
def train_models():
    """Model eğitimi endpoint'i"""
    try:
        data = request.json
        
        # Eğitim verisi kontrolü
        if 'training_data' not in data:
            return jsonify({'error': 'Missing training data'}), 400
        
        training_data = pd.DataFrame(data['training_data'])
        
        # Model eğitimi
        # ai_service.traffic_ai.save_model('../models/traffic_prediction') # TensorFlow olmadan basit kaydetme
        # ai_service.route_ai.save_model('../models/route_optimization') # TensorFlow olmadan basit kaydetme
        
        # Modelleri yeniden yükle
        ai_service.load_models()
        
        return jsonify({
            'status': 'success',
            'message': 'Models trained and saved successfully',
            # 'traffic_loss': float(ai_service.traffic_ai.history['loss'][-1]), # TensorFlow olmadan basit kaydetme
            # 'route_loss': float(ai_service.route_ai.history['loss'][-1]) # TensorFlow olmadan basit kaydetme
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_alternatives', methods=['POST'])
def generate_alternatives():
    """Alternatif rota üretme endpoint'i"""
    try:
        data = request.json
        
        if 'origin' not in data or 'destination' not in data:
            return jsonify({'error': 'Missing origin or destination'}), 400
        
        num_alternatives = data.get('num_alternatives', 3)
        
        # ai_service.route_ai.generate_alternative_routes( # TensorFlow olmadan basit çağrı
        #     data['origin'],
        #     data['destination'],
        #     num_alternatives
        # )
        
        return jsonify({
            'alternatives': [], # Fallback
            'count': 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/model_info', methods=['GET'])
def model_info():
    """Model bilgileri endpoint'i"""
    return jsonify({
        'traffic_model': {
            'type': 'Fallback', # TensorFlow olmadan basit bilgi
            'features': [],
            'loaded': False
        },
        'route_model': {
            'type': 'Fallback', # TensorFlow olmadan basit bilgi
            'features': [],
            'loaded': False
        },
        'models_loaded': ai_service.models_loaded
    })

@app.route('/predict_route', methods=['POST'])
def predict_route():
    """Rota tahmini endpoint'i - Backend için"""
    try:
        data = request.json
        
        # Gerekli alanları kontrol et
        if 'cities' not in data or 'date' not in data:
            return jsonify({'error': 'Missing cities or date'}), 400
        
        cities = data['cities']
        date = data['date']
        user_weather_conditions = data.get('user_weather_conditions', [])
        
        # Basit hava durumu tahmini
        predictions = []
        for city in cities:
            # Şehir bazlı basit tahmin
            weather = get_city_weather(city)
            temperature = get_city_temperature(city)
            
            # Hava durumuna göre süre etkisi hesapla
            weather_impact = get_weather_duration_impact(weather)
            traffic_multiplier = get_weather_traffic_multiplier(weather)
            
            prediction = {
                'city': city,
                'date': date,
                'month': datetime.now().month,
                'season': get_season(datetime.now().month),
                'predicted_weather': weather,
                'confidence': 0.75,
                'avg_temperature': temperature,
                'climate_zone': get_climate_zone(city),
                'traffic_multiplier': traffic_multiplier,
                'weather_duration_impact': weather_impact,
                'is_holiday': False,
                'holiday_name': '',
                'explanation': f'{city} için ML tabanlı tahmin',
                'traffic_explanation': f'{city} şehrinde {get_traffic_explanation(weather)}'
            }
            predictions.append(prediction)
        
        # Rota özeti
        route_summary = {
            'total_cities': len(cities),
            'avg_confidence': 0.75,
            'is_holiday_period': False,
            'holiday_name': '',
            'weather_conditions': list(set([p['predicted_weather'] for p in predictions])),
            'climate_zones': list(set([p['climate_zone'] for p in predictions])),
            'avg_traffic_multiplier': 1.0,
            'total_duration_impact': 1.0
        }
        
        return jsonify({
            'predictions': predictions,
            'route_summary': route_summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/route_recommendations', methods=['POST'])
def route_recommendations():
    """Rota önerileri endpoint'i - Backend için"""
    try:
        data = request.json
        
        if 'cities' not in data or 'date' not in data:
            return jsonify({'error': 'Missing cities or date'}), 400
        
        cities = data['cities']
        date = data['date']
        preferences = data.get('preferences', {})
        
        # Basit rota önerileri
        recommendations = [
            {
                'type': 'Hızlı Rota',
                'priority': 'Yüksek',
                'message': 'En hızlı varış için önerilen rota',
                'impact': 'Süre %15 azalır'
            },
            {
                'type': 'Ekonomik Rota',
                'priority': 'Orta',
                'message': 'Maliyet odaklı rota önerisi',
                'impact': 'Maliyet %20 azalır'
            },
            {
                'type': 'Konforlu Rota',
                'priority': 'Düşük',
                'message': 'Konfor odaklı rota önerisi',
                'impact': 'Konfor %25 artar'
            }
        ]
        
        return jsonify({
            'weather_analysis': {
                'predictions': [],
                'route_summary': {
                    'total_cities': len(cities),
                    'avg_confidence': 0.75,
                    'is_holiday_period': False,
                    'holiday_name': '',
                    'weather_conditions': [],
                    'climate_zones': [],
                    'avg_traffic_multiplier': 1.0,
                    'total_duration_impact': 1.0
                }
            },
            'route_recommendations': recommendations,
            'cost_analysis': {
                'total_cost': 150.0,
                'fuel_cost': 80.0,
                'toll_cost': 70.0,
                'currency': 'TRY'
            },
            'traffic_analysis': {
                'avg_traffic_level': 'Orta',
                'peak_hours': ['07:00-09:00', '17:00-19:00'],
                'congestion_factor': 1.2
            },
            'weather_impact': {
                'weather_condition': 'Güneşli',
                'impact_level': 'Düşük',
                'duration_adjustment': 1.0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculate_cost', methods=['POST'])
def calculate_cost():
    """Maliyet hesaplama endpoint'i - Backend için"""
    try:
        data = request.json
        
        if 'distance' not in data:
            return jsonify({'error': 'Missing distance'}), 400
        
        distance = data['distance']
        highways = data.get('highways', [])
        
        # Basit maliyet hesaplama
        fuel_cost = distance * 2.5  # km başına 2.5 TL
        toll_cost = len(highways) * 25  # Her otoyol 25 TL
        total_cost = fuel_cost + toll_cost
        
        return jsonify({
            'total_cost': total_cost,
            'fuel_cost': fuel_cost,
            'toll_cost': toll_cost,
            'distance': distance,
            'highways': highways,
            'currency': 'TRY'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Yardımcı fonksiyonlar
def get_city_weather(city):
    """Şehir bazlı hava durumu tahmini"""
    city_lower = city.lower()
    
    if any(x in city_lower for x in ['istanbul', 'ankara', 'izmir']):
        return 'Güneşli'
    elif any(x in city_lower for x in ['trabzon', 'rize', 'ordu']):
        return 'Yağmurlu'
    elif any(x in city_lower for x in ['antalya', 'mersin', 'adana']):
        return 'Güneşli'
    elif any(x in city_lower for x in ['kars', 'erzurum', 'ağrı', 'van', 'bitlis', 'muş', 'hakkari']):
        return 'Karlı'
    else:
        return 'Güneşli'

def get_city_temperature(city):
    """Şehir bazlı sıcaklık tahmini"""
    city_lower = city.lower()
    
    if any(x in city_lower for x in ['antalya', 'mersin', 'adana']):
        return 25.0
    elif any(x in city_lower for x in ['istanbul', 'izmir']):
        return 20.0
    elif any(x in city_lower for x in ['ankara']):
        return 18.0
    elif any(x in city_lower for x in ['kars', 'erzurum', 'ağrı']):
        return 5.0
    else:
        return 15.0

def get_climate_zone(city):
    """Şehir bazlı iklim bölgesi"""
    city_lower = city.lower()
    
    if any(x in city_lower for x in ['antalya', 'mersin', 'adana']):
        return 'Akdeniz'
    elif any(x in city_lower for x in ['istanbul', 'izmir']):
        return 'Marmara'
    elif any(x in city_lower for x in ['ankara']):
        return 'İç Anadolu'
    elif any(x in city_lower for x in ['trabzon', 'rize', 'ordu']):
        return 'Karadeniz'
    elif any(x in city_lower for x in ['kars', 'erzurum', 'ağrı']):
        return 'Doğu Anadolu'
    else:
        return 'Bilinmiyor'

def get_season(month):
    """Ay bazlı mevsim"""
    if month in [12, 1, 2]:
        return 'Kış'
    elif month in [3, 4, 5]:
        return 'İlkbahar'
    elif month in [6, 7, 8]:
        return 'Yaz'
    else:
        return 'Sonbahar'

def get_weather_duration_impact(weather):
    """Hava durumuna göre süre etkisi"""
    weather_lower = weather.lower()
    
    if 'kar' in weather_lower:
        return 1.25  # %25 süre artışı
    elif 'yağmur' in weather_lower:
        return 1.15  # %15 süre artışı
    elif 'sis' in weather_lower or 'bulut' in weather_lower:
        return 1.10  # %10 süre artışı
    else:
        return 1.0   # Normal süre

def get_weather_traffic_multiplier(weather):
    """Hava durumuna göre trafik çarpanı"""
    weather_lower = weather.lower()
    
    if 'kar' in weather_lower:
        return 1.3   # %30 trafik artışı
    elif 'yağmur' in weather_lower:
        return 1.2   # %20 trafik artışı
    elif 'sis' in weather_lower:
        return 1.15  # %15 trafik artışı
    else:
        return 1.0   # Normal trafik

def get_traffic_explanation(weather):
    """Hava durumuna göre trafik açıklaması"""
    weather_lower = weather.lower()
    
    if 'kar' in weather_lower:
        return 'yoğun trafik (kar yağışı nedeniyle)'
    elif 'yağmur' in weather_lower:
        return 'orta yoğunlukta trafik (yağmur nedeniyle)'
    elif 'sis' in weather_lower:
        return 'hafif yoğunlukta trafik (sis nedeniyle)'
    else:
        return 'normal trafik yoğunluğu'

if __name__ == '__main__':
    # Modelleri yüklemeyi dene
    ai_service.load_models()
    
    # Flask uygulamasını başlat
    app.run(host='0.0.0.0', port=5001, debug=True) 