from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
import json
import os

app = Flask(__name__)

class AIService:
    def __init__(self):
      
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




if __name__ == '__main__':
    # Modelleri yüklemeyi dene
    ai_service.load_models()
    
    # Flask uygulamasını başlat
    app.run(host='0.0.0.0', port=5001, debug=True) 