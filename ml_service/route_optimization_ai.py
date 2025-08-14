import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import json
import os
from datetime import datetime, timedelta

class RouteOptimizationAI:
    def __init__(self):
        self.duration_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.cost_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.comfort_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.history = {'loss': [0.5]}  # Fallback history
        
    def create_sequences(self, data):
        """Veri dizilerini oluştur"""
        sequences = []
        duration_targets = []
        cost_targets = []
        comfort_targets = []
        
        # 24 saatlik sekanslar oluştur
        for i in range(24, len(data)):
            sequence = data.iloc[i-24:i][['hour', 'day_of_week', 'month', 'weather_code', 'distance']].values
            sequences.append(sequence.flatten())
            duration_targets.append(data.iloc[i]['duration'])
            cost_targets.append(data.iloc[i]['cost'])
            comfort_targets.append(data.iloc[i]['comfort_score'])
        
        return np.array(sequences), np.array(duration_targets), np.array(cost_targets), np.array(comfort_targets)
    
    def train(self, training_data):
        """Modeli eğit"""
        print(" Rota optimizasyon modeli eğitiliyor...")
        
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
        X, y_duration, y_cost, y_comfort = self.create_sequences(data)
        
        if len(X) == 0:
            print("⚠️ Yeterli veri yok, fallback model kullanılıyor")
            return self
        
        # Veriyi böl
        X_train, X_test, y_duration_train, y_duration_test, y_cost_train, y_cost_test, y_comfort_train, y_comfort_test = train_test_split(
            X, y_duration, y_cost, y_comfort, test_size=0.2, random_state=42
        )
        
        # Ölçeklendirme
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Modelleri eğit
        self.duration_model.fit(X_train_scaled, y_duration_train)
        self.cost_model.fit(X_train_scaled, y_cost_train)
        self.comfort_model.fit(X_train_scaled, y_comfort_train)
        
        # Performans değerlendirme
        duration_score = self.duration_model.score(X_test_scaled, y_duration_test)
        cost_score = self.cost_model.score(X_test_scaled, y_cost_test)
        comfort_score = self.comfort_model.score(X_test_scaled, y_comfort_test)
        
        self.is_trained = True
        self.history = {'loss': [1 - (duration_score + cost_score + comfort_score) / 3]}
        
        print(f" Model eğitildi! Duration: {duration_score:.3f}, Cost: {cost_score:.3f}, Comfort: {comfort_score:.3f}")
        return self
    
    def optimize_route(self, route_info, weather_data, traffic_data, user_preferences):
        """Rota optimizasyonu"""
        if not self.is_trained:
            return self._fallback_optimization(route_info, weather_data, traffic_data, user_preferences)
        
        try:
            # Özellik vektörü oluştur
            features = [
                datetime.now().hour,
                datetime.now().weekday(),
                datetime.now().month,
                self._get_weather_code(weather_data.get('condition', 'güneş')),
                route_info.get('distance', 100)
            ]
            
            # 24 saatlik sekans oluştur (basitleştirilmiş)
            sequence = np.array(features * 5)  # 24 özellik için 5 kez tekrarla
            
            # Ölçeklendirme ve tahmin
            sequence_scaled = self.scaler.transform([sequence])
            duration = self.duration_model.predict(sequence_scaled)[0]
            cost = self.cost_model.predict(sequence_scaled)[0]
            comfort = self.comfort_model.predict(sequence_scaled)[0]
            
            # Hava durumu etkisi
            weather_impact = self._calculate_weather_impact(weather_data.get('condition', ''))
            
            # Trafik etkisi
            traffic_multiplier = traffic_data.get('traffic_multiplier', 1.0)
            
            # Sonuçları hesapla
            final_duration = duration * weather_impact * traffic_multiplier
            final_cost = cost * weather_impact
            final_comfort = max(0.1, min(1.0, comfort / weather_impact))
            
            return {
                'duration': max(10, final_duration),  # Minimum 10 dakika
                'cost': max(0, final_cost),
                'comfort_score': final_comfort,
                'weather_impact': weather_impact,
                'traffic_impact': traffic_multiplier,
                'optimization_score': self._calculate_optimization_score(
                    final_duration, final_cost, final_comfort, user_preferences
                )
            }
            
        except Exception as e:
            print(f"AI optimizasyon hatası: {e}")
            return self._fallback_optimization(route_info, weather_data, traffic_data, user_preferences)
    
    def _fallback_optimization(self, route_info, weather_data, traffic_data, user_preferences):
        """Fallback optimizasyon (rule-based)"""
        base_duration = route_info.get('distance', 100) * 1.5  # km başına 1.5 dakika
        base_cost = route_info.get('distance', 100) * 0.5  # km başına 0.5 TL
        base_comfort = 0.8
        
        # Hava durumu etkisi
        weather_impact = self._calculate_weather_impact(weather_data.get('condition', ''))
        
        # Trafik etkisi
        traffic_multiplier = traffic_data.get('traffic_multiplier', 1.0)
        
        final_duration = base_duration * weather_impact * traffic_multiplier
        final_cost = base_cost * weather_impact
        final_comfort = max(0.1, min(1.0, base_comfort / weather_impact))
        
        return {
            'duration': final_duration,
            'cost': final_cost,
            'comfort_score': final_comfort,
            'weather_impact': weather_impact,
            'traffic_impact': traffic_multiplier,
            'optimization_score': 0.6
        }
    
    def _calculate_weather_impact(self, condition):
        """Hava durumu etkisini hesapla"""
        condition = condition.lower()
        
        if 'yağmur' in condition or 'yağmurlu' in condition:
            return 1.1  # %10 artış
        elif 'kar' in condition or 'karlı' in condition:
            return 1.15  # %15 artış
        elif 'fırtına' in condition:
            return 1.12  # %12 artış
        elif 'rüzgar' in condition:
            return 1.03  # %3 artış
        elif 'sis' in condition or 'sisli' in condition:
            return 1.08  # %8 artış
        elif 'bulutlu' in condition:
            return 1.02  # %2 artış
        elif 'güneş' in condition or 'güneşli' in condition:
            return 1.0  # Etki yok
        else:
            return 1.0
    
    def _calculate_optimization_score(self, duration, cost, comfort, preferences):
        """Optimizasyon skorunu hesapla"""
        duration_weight = preferences.get('duration_weight', 0.4)
        cost_weight = preferences.get('cost_weight', 0.3)
        comfort_weight = preferences.get('comfort_weight', 0.3)
        
        # Normalize değerler (0-1 arası)
        norm_duration = max(0, min(1, 1 - (duration - 30) / 300))  # 30-330 dakika arası
        norm_cost = max(0, min(1, 1 - cost / 500))  # 0-500 TL arası
        norm_comfort = comfort  # Zaten 0-1 arası
        
        score = (norm_duration * duration_weight + 
                norm_cost * cost_weight + 
                norm_comfort * comfort_weight)
        
        return max(0, min(1, score))
    
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
            
            # Modelleri kaydet
            joblib.dump(self.duration_model, f"{filepath}_duration_model.pkl")
            joblib.dump(self.cost_model, f"{filepath}_cost_model.pkl")
            joblib.dump(self.comfort_model, f"{filepath}_comfort_model.pkl")
            joblib.dump(self.scaler, f"{filepath}_scaler.pkl")
            
            # Metadata kaydet
            metadata = {
                'model_type': 'RandomForest_RouteOptimization',
                'is_trained': self.is_trained,
                'created_at': datetime.now().isoformat(),
                'features': ['hour', 'day_of_week', 'month', 'weather_code', 'distance']
            }
            
            with open(f"{filepath}_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f" Model kaydedildi: {filepath}")
            
        except Exception as e:
            print(f"Model kaydetme hatası: {e}")
    
    def load_model(self, filepath):
        """Modeli yükle"""
        try:
            # Modelleri yükle
            self.duration_model = joblib.load(f"{filepath}_duration_model.pkl")
            self.cost_model = joblib.load(f"{filepath}_cost_model.pkl")
            self.comfort_model = joblib.load(f"{filepath}_comfort_model.pkl")
            self.scaler = joblib.load(f"{filepath}_scaler.pkl")
            
            # Metadata kontrolü
            if os.path.exists(f"{filepath}_metadata.json"):
                with open(f"{filepath}_metadata.json", 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self.is_trained = metadata.get('is_trained', False)
            
            print(f" Model yüklendi: {filepath}")
            return True
            
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            return False

if __name__ == "__main__":
    # Test kodu
    print(" Rota Optimizasyon AI Model Test Ediliyor...")
    
    # Örnek veri oluştur
    test_data = []
    for i in range(100):  # 100 satır test verisi
        timestamp = datetime.now() + timedelta(hours=i)
        test_data.append({
            'timestamp': timestamp.isoformat(),
            'duration': 60 + (i % 5) * 30,  # 60-240 dakika
            'cost': 50 + (i % 10) * 20,     # 50-230 TL
            'comfort_score': 0.5 + (i % 3) * 0.2,  # 0.5-0.9
            'weather_condition': ['güneş', 'yağmur', 'bulutlu'][i % 3],
            'distance': 50 + (i % 10) * 20  # 50-230 km
        })
    
    # Model oluştur ve eğit
    route_ai = RouteOptimizationAI()
    route_ai.train(test_data)
    
    # Test optimizasyonu
    test_route = {'distance': 150}
    test_weather = {'condition': 'yağmurlu'}
    test_traffic = {'traffic_multiplier': 1.2}
    test_preferences = {'duration_weight': 0.4, 'cost_weight': 0.3, 'comfort_weight': 0.3}
    
    optimization = route_ai.optimize_route(test_route, test_weather, test_traffic, test_preferences)
    
    print(f" Test optimizasyonu:")
    print(f"   Süre: {optimization['duration']:.1f} dakika")
    print(f"   Maliyet: {optimization['cost']:.1f} TL")
    print(f"   Konfor: {optimization['comfort_score']:.2f}")
    print(f"   Skor: {optimization['optimization_score']:.2f}")
    print(" Test tamamlandı!") 