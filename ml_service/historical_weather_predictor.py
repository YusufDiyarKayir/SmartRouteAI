"""
Tarihsel Veri Tabanlı Hava Durumu Tahmin Sistemi

Bu modül, gerçek tarihsel hava durumu verilerini kullanarak
gün bazında olasılık hesaplamaları yapar ve ML modellerini eğitir.

Özellikler:
- Gerçek tarihsel verilerle olasılık hesaplama
- Gün bazında hava durumu tahmini
- ML modelleri için eğitim verisi
- Yüksek doğruluk oranı
"""

from historical_weather_data import HistoricalWeatherDataCollector
from flask import Flask, request, jsonify
from flask_cors import CORS #(Cross-Origin Resource Sharing)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

class HistoricalWeatherPredictor:
    def __init__(self):
        self.collector = HistoricalWeatherDataCollector()
        self.weather_model = None
        self.temperature_model = None
        self.scaler = StandardScaler()
        self.weather_encoder = LabelEncoder()
        
        # Model dosyalarının yolları
        self.model_files = [
            '../models/historical_weather_model.pkl',
            '../models/historical_temperature_model.pkl',
            '../models/historical_scaler.pkl',
            '../models/historical_weather_encoder.pkl'
        ]
        
        # Modelleri yükle veya eğit
        self.load_or_train_models()
        
        print("🌤️ Tarihsel Veri Tabanlı Hava Durumu Tahmin Sistemi Başlatıldı")
    
    def load_or_train_models(self):
        """ML modellerini yükle veya eğit"""
        # Model dosyalarının varlığını kontrol et
        if all(os.path.exists(f) for f in self.model_files):
            try:
                self.weather_model = joblib.load(self.model_files[0])
                self.temperature_model = joblib.load(self.model_files[1])
                self.scaler = joblib.load(self.model_files[2])
                self.weather_encoder = joblib.load(self.model_files[3])
                print("✅ Tarihsel veri modelleri yüklendi")
                return
            except Exception as e:
                print(f"❌ Model yükleme hatası: {e}")
        
        print("🤖 Tarihsel veri modelleri eğitiliyor...")
        self.train_models()
    
    def train_models(self):
        """ML modellerini eğit"""
        try:
            # Eğitim verisini al
            training_data = self.collector.generate_training_data()
            
            if training_data.empty:
                print("❌ Eğitim verisi bulunamadı!")
                return
            
            print(f"📊 Eğitim verisi: {len(training_data)} kayıt")
            
            # Özellikleri hazırla
            features = self._prepare_features(training_data)
            
            # Hava durumu sınıflandırma modeli
            X_weather = features.drop(['weather_main', 'temperature'], axis=1, errors='ignore')
            y_weather = self.weather_encoder.fit_transform(training_data['weather_main'])
            
            # Sıcaklık regresyon modeli
            X_temp = features.drop(['weather_main', 'temperature'], axis=1, errors='ignore')
            y_temp = training_data['temperature']
            
            # Veriyi eğitim ve test olarak böl
            X_weather_train, X_weather_test, y_weather_train, y_weather_test = train_test_split(
                X_weather, y_weather, test_size=0.2, random_state=42
            )
            
            X_temp_train, X_temp_test, y_temp_train, y_temp_test = train_test_split(
                X_temp, y_temp, test_size=0.2, random_state=42
            )
            
            # Modelleri eğit
            print("🌤️ Hava durumu sınıflandırma modeli eğitiliyor...")
            self.weather_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.weather_model.fit(X_weather_train, y_weather_train)
            
            print("🌡️ Sıcaklık regresyon modeli eğitiliyor...")
            self.temperature_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.temperature_model.fit(X_temp_train, y_temp_train)
            
            # Model performansını değerlendir
            weather_accuracy = accuracy_score(y_weather_test, self.weather_model.predict(X_weather_test))
            temp_r2 = self.temperature_model.score(X_temp_test, y_temp_test)
            
            print(f"✅ Hava durumu modeli doğruluğu: {weather_accuracy:.3f}")
            print(f"✅ Sıcaklık modeli R² skoru: {temp_r2:.3f}")
            
            # Modelleri kaydet
            os.makedirs('../models', exist_ok=True)
            joblib.dump(self.weather_model, self.model_files[0])
            joblib.dump(self.temperature_model, self.model_files[1])
            joblib.dump(self.scaler, self.model_files[2])
            joblib.dump(self.weather_encoder, self.model_files[3])
            
            print("💾 Modeller kaydedildi")
            
        except Exception as e:
            print(f"❌ Model eğitimi hatası: {e}")
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """ML modelleri için özellikleri hazırla"""
        features = data.copy()
        
        # Tarih özellikleri
        features['date'] = pd.to_datetime(features['date'])
        features['month'] = features['date'].dt.month
        features['day'] = features['date'].dt.day
        features['day_of_year'] = features['date'].dt.dayofyear
        features['day_of_week'] = features['date'].dt.dayofweek
        
        # Mevsim özellikleri
        features['season'] = features['month'].map({
            12: 0, 1: 0, 2: 0,  # Kış
            3: 1, 4: 1, 5: 1,   # İlkbahar
            6: 2, 7: 2, 8: 2,   # Yaz
            9: 3, 10: 3, 11: 3  # Sonbahar
        })
        
        # Coğrafi özellikler
        features['latitude'] = features['latitude'].fillna(39.0)
        features['longitude'] = features['longitude'].fillna(35.0)
        
        # Eksik değerleri doldur
        features['humidity'] = features['humidity'].fillna(50)
        features['wind_speed'] = features['wind_speed'].fillna(10)
        features['probability'] = features['probability'].fillna(0.5)
        features['sample_count'] = features['sample_count'].fillna(1)
        
        # Sayısal özellikleri seç
        numeric_features = [
            'month', 'day', 'day_of_year', 'day_of_week', 'season',
            'latitude', 'longitude', 'humidity', 'wind_speed', 
            'probability', 'sample_count'
        ]
        
        return features[numeric_features + ['weather_main', 'temperature']]
    
    def predict_weather(self, city: str, date_str: str) -> Dict:
        """Belirli bir şehir ve tarih için hava durumu tahmini"""
        try:
            # Tarihi parse et
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            month = date_obj.month
            day = date_obj.day
            
            # Tarihsel olasılıkları al
            historical_prob = self.collector.get_daily_weather_probability(city, month, day)
            
            # Geçmiş örnekleri al
            historical_examples = self.collector.get_historical_examples(city, month, day, limit=5)
            
            # ML modeli için özellikleri hazırla
            city_coords = self.collector.cities_data.get(city, {"lat": 39.0, "lon": 35.0})
            
            features = pd.DataFrame([{
                'month': month,
                'day': day,
                'day_of_year': date_obj.timetuple().tm_yday,
                'day_of_week': date_obj.weekday(),
                'season': (month % 12 + 3) // 3,
                'latitude': city_coords['lat'],
                'longitude': city_coords['lon'],
                'humidity': np.mean([ex['humidity'] for ex in historical_examples]) if historical_examples else 50,
                'wind_speed': np.mean([ex['wind_speed'] for ex in historical_examples]) if historical_examples else 10,
                'probability': historical_prob.get('confidence', 0.5),
                'sample_count': historical_prob.get('sample_count', 1)
            }])
            
            # ML tahminleri
            if self.weather_model is not None:
                weather_pred = self.weather_encoder.inverse_transform(
                    self.weather_model.predict(features)
                )[0]
                weather_proba = self.weather_model.predict_proba(features)[0]
                ml_confidence = max(weather_proba)
            else:
                weather_pred = historical_prob.get('most_likely', 'Unknown')
                ml_confidence = 0.5
            
            if self.temperature_model is not None:
                predicted_temp = self.temperature_model.predict(features)[0]
            else:
                predicted_temp = np.mean([ex['temperature'] for ex in historical_examples]) if historical_examples else 20
            
            # Sonuçları birleştir
            result = {
                "city": city,
                "date": date_str,
                "predicted_weather": weather_pred,
                "predicted_temperature": round(predicted_temp, 1),
                "historical_probabilities": historical_prob.get('weather_probabilities', {}),
                "historical_examples": historical_examples,
                "ml_confidence": ml_confidence,
                "historical_confidence": historical_prob.get('confidence', 0.0),
                "sample_count": historical_prob.get('sample_count', 0),
                "explanation": self._generate_explanation(city, month, day, historical_prob, historical_examples)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Hava durumu tahmin hatası: {e}")
            return self._get_fallback_prediction(city, date_str)
    
    def _generate_explanation(self, city: str, month: int, day: int, 
                            historical_prob: Dict, historical_examples: List[Dict]) -> str:
        """Tahmin için açıklama oluştur"""
        if not historical_examples:
            return f"{city} için {month}/{day} tarihinde yeterli tarihsel veri bulunamadı."
        
        # En sık görülen hava durumları
        weather_counts = {}
        for example in historical_examples:
            weather = example['weather']
            weather_counts[weather] = weather_counts.get(weather, 0) + 1
        
        most_common = max(weather_counts.items(), key=lambda x: x[1])
        
        # Sıcaklık ortalaması
        avg_temp = np.mean([ex['temperature'] for ex in historical_examples])
        
        explanation = f"{city} için {month}/{day} tarihinde son {len(historical_examples)} yılda "
        explanation += f"en sık {most_common[0]} hava durumu görülmüş ({most_common[1]} kez). "
        explanation += f"Ortalama sıcaklık {avg_temp:.1f}°C. "
        
        if historical_prob.get('weather_probabilities'):
            top_prob = max(historical_prob['weather_probabilities'].items(), 
                          key=lambda x: x[1]['probability'])
            explanation += f"Tarihsel olasılık hesaplamasına göre %{top_prob[1]['probability']*100:.0f} "
            explanation += f"{top_prob[0]} olasılığı var."
        
        return explanation
    
    def _get_fallback_prediction(self, city: str, date_str: str) -> Dict:
        """Fallback tahmin"""
        return {
            "city": city,
            "date": date_str,
            "predicted_weather": "Unknown",
            "predicted_temperature": 20.0,
            "historical_probabilities": {},
            "historical_examples": [],
            "ml_confidence": 0.0,
            "historical_confidence": 0.0,
            "sample_count": 0,
            "explanation": "Yeterli veri bulunamadığı için tahmin yapılamadı."
        }
    
    def predict_route_weather(self, cities: List[str], date_str: str) -> Dict:
        """Rota üzerindeki tüm şehirler için hava durumu tahmini"""
        predictions = []
        total_confidence = 0
        
        for city in cities:
            prediction = self.predict_weather(city, date_str)
            predictions.append(prediction)
            total_confidence += prediction.get('ml_confidence', 0)
        
        avg_confidence = total_confidence / len(cities) if cities else 0
        
        return {
            "predictions": predictions,
            "route_summary": {
                "total_cities": len(cities),
                "avg_confidence": avg_confidence,
                "weather_conditions": list(set([p["predicted_weather"] for p in predictions])),
                "avg_temperature": sum([p["predicted_temperature"] for p in predictions]) / len(predictions) if predictions else 20.0
            }
        }
    
    def get_city_statistics(self, city: str) -> Dict:
        """Şehir için istatistiksel bilgiler"""
        return self.collector.get_city_statistics(city)

# Flask API
app = Flask(__name__)
CORS(app)  # CORS desteği ekle
predictor = HistoricalWeatherPredictor()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Historical Weather Predictor",
        "models_loaded": predictor.weather_model is not None and predictor.temperature_model is not None,
        "cities_supported": len(predictor.collector.cities_data)
    })

@app.route('/predict', methods=['POST'])
def predict_weather():
    try:
        data = request.get_json()
        city = data.get('city')
        date = data.get('date')
        
        if not city or not date:
            return jsonify({"error": "city ve date parametreleri gerekli"}), 400
        
        prediction = predictor.predict_weather(city, date)
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict_route', methods=['POST'])
def predict_route():
    try:
        data = request.get_json()
        cities = data.get('cities', [])
        date = data.get('date')
        
        if not cities or not date:
            return jsonify({"error": "cities ve date parametreleri gerekli"}), 400
        
        prediction = predictor.predict_route_weather(cities, date)
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/statistics/<city>', methods=['GET'])
def get_city_statistics(city):
    try:
        stats = predictor.get_city_statistics(city)
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Tarihsel Veri Tabanlı Hava Durumu Tahmin Servisi Başlatılıyor...")
    print("📊 Örnek kullanım:")
    print("  POST /predict - Tek şehir tahmini")
    print("  POST /predict_route - Rota tahmini")
    print("  GET /statistics/<city> - Şehir istatistikleri")
    
    app.run(host='0.0.0.0', port=5002, debug=True) 