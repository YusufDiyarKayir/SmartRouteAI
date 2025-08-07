import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import json
import os
from datetime import datetime, timedelta

class TrafficPredictionAI:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.history = {'loss': [0.5]}  # Fallback history
        
    def create_sequences(self, data, target_col='traffic_level'):
        """Veri dizilerini oluştur"""
        sequences = []
        targets = []
        
        # 24 saatlik sekanslar oluştur
        for i in range(24, len(data)):
            sequence = data.iloc[i-24:i][['hour', 'day_of_week', 'month', 'weather_code']].values
            target = data.iloc[i][target_col]
            sequences.append(sequence.flatten())
            targets.append(target)
        
        return np.array(sequences), np.array(targets)
    
    def train(self, training_data):
        """Modeli eğit"""
        print("🤖 Trafik tahmin modeli eğitiliyor...")
        
        # Veri hazırlama
        data = pd.DataFrame(training_data)
        
        # Özellik mühendisliği
        data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
        data['day_of_week'] = pd.to_datetime(data['timestamp']).dt.dayofweek
        data['month'] = pd.to_datetime(data['timestamp']).dt.month
        data['weather_code'] = data['weather_condition'].map({
            'güneş': 1, 'yağmur': 2, 'kar': 3, 'bulutlu': 4, 'sis': 5, 'fırtına': 6, 'rüzgar': 7
        }).fillna(1)
        
        # Sekanslar oluştur
        X, y = self.create_sequences(data)
        
        if len(X) == 0:
            print("⚠️ Yeterli veri yok, fallback model kullanılıyor")
            return self
        
        # Veriyi böl
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Ölçeklendirme
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Model eğitimi
        self.model.fit(X_train_scaled, y_train)
        
        # Performans değerlendirme
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        self.is_trained = True
        self.history = {'loss': [1 - test_score]}
        
        print(f"✅ Model eğitildi! Train Score: {train_score:.3f}, Test Score: {test_score:.3f}")
        return self
    
    def predict_traffic(self, route_info, weather_data, date_time):
        """Trafik tahmini yap"""
        if not self.is_trained:
            return self._fallback_prediction(route_info, weather_data, date_time)
        
        try:
            # Özellik vektörü oluştur
            features = [
                date_time.hour,
                date_time.weekday(),
                date_time.month,
                self._get_weather_code(weather_data.get('condition', 'güneş'))
            ]
            
            # 24 saatlik sekans oluştur (basitleştirilmiş)
            sequence = np.array(features * 6)  # 24 özellik için 6 kez tekrarla
            
            # Ölçeklendirme ve tahmin
            sequence_scaled = self.scaler.transform([sequence])
            prediction = self.model.predict(sequence_scaled)[0]
            
            return max(0.5, min(3.0, prediction))  # 0.5-3.0 arası sınırla
            
        except Exception as e:
            print(f"AI tahmin hatası: {e}")
            return self._fallback_prediction(route_info, weather_data, date_time)
    
    def _fallback_prediction(self, route_info, weather_data, date_time):
        """Fallback tahmin (rule-based)"""
        base_multiplier = 1.0
        
        # Hafta sonu etkisi
        if date_time.weekday() >= 5:
            base_multiplier *= 1.2
        
        # Hava durumu etkisi
        weather_condition = weather_data.get('condition', '').lower()
        if 'yağmur' in weather_condition:
            base_multiplier *= 1.08
        elif 'kar' in weather_condition:
            base_multiplier *= 1.12
        
        return base_multiplier
    
    def _get_weather_code(self, condition):
        """Hava durumu kodunu döndür"""
        weather_map = {
            'güneş': 1, 'yağmur': 2, 'kar': 3, 'bulutlu': 4, 
            'sis': 5, 'fırtına': 6, 'rüzgar': 7
        }
        return weather_map.get(condition.lower(), 1)
    
    def save_model(self, filepath):
        """Modeli kaydet"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Model ve scaler'ı kaydet
            joblib.dump(self.model, f"{filepath}_model.pkl")
            joblib.dump(self.scaler, f"{filepath}_scaler.pkl")
            
            # Metadata kaydet
            metadata = {
                'model_type': 'RandomForest',
                'is_trained': self.is_trained,
                'created_at': datetime.now().isoformat(),
                'features': ['hour', 'day_of_week', 'month', 'weather_code']
            }
            
            with open(f"{filepath}_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Model kaydedildi: {filepath}")
            
        except Exception as e:
            print(f"Model kaydetme hatası: {e}")
    
    def load_model(self, filepath):
        """Modeli yükle"""
        try:
            # Model ve scaler'ı yükle
            self.model = joblib.load(f"{filepath}_model.pkl")
            self.scaler = joblib.load(f"{filepath}_scaler.pkl")
            
            # Metadata kontrolü
            if os.path.exists(f"{filepath}_metadata.json"):
                with open(f"{filepath}_metadata.json", 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self.is_trained = metadata.get('is_trained', False)
            
            print(f"📁 Model yüklendi: {filepath}")
            return True
            
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            return False

 