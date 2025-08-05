
import json
import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import os
from typing import Dict, List, Tuple
import random

#ML hava durumu veritabanı sınıfı
class MLWeatherDatabase:
    def __init__(self):
        self.weather_model = None #Hava durumu modeli
        self.temperature_model = None #Sıcaklık modeli
        self.traffic_model = None #Trafik modeli
        self.scaler = StandardScaler() #Ölçekleyici
        self.weather_encoder = LabelEncoder() #Hava durumu kodlayıcı
        self.climate_encoder = LabelEncoder() #İklim kodlayıcı
        
        # Türkiye şehirleri coğrafi verileri
        self.cities_data = self._load_cities_geographic_data()
        
        # Modelleri yükle veya eğit
        self.load_or_train_models()
                
        print("🤖 ML Tabanlı Hava Durumu Sistemi Başlatıldı")
        print(f"📊 {len(self.cities_data)} şehir için ML modelleri hazır")
    
    def _load_cities_geographic_data(self) -> Dict:
        """Türkiye şehirlerinin coğrafi ve iklim verileri"""
        return {
            # Marmara 
            "İstanbul": {"lat": 41.0082, "lon": 28.9784, "elevation": 100, "climate": "Marmara", "population": 15520000},
            "Bursa": {"lat": 40.1885, "lon": 29.0610, "elevation": 100, "climate": "Marmara", "population": 3101833},
            "Sakarya": {"lat": 40.7569, "lon": 30.3781, "elevation": 31, "climate": "Marmara", "population": 1025278},
            "Kocaeli": {"lat": 40.8533, "lon": 29.8815, "elevation": 100, "climate": "Marmara", "population": 1994442},
            "Tekirdağ": {"lat": 40.9780, "lon": 27.5110, "elevation": 28, "climate": "Marmara", "population": 1111915},
            "Edirne": {"lat": 41.6771, "lon": 26.5557, "elevation": 42, "climate": "Marmara", "population": 411528},
            "Kırklareli": {"lat": 41.7351, "lon": 27.2250, "elevation": 203, "climate": "Marmara", "population": 361737},
            "Balıkesir": {"lat": 39.6484, "lon": 27.8826, "elevation": 70, "climate": "Marmara", "population": 1240285},
            "Çanakkale": {"lat": 40.1553, "lon": 26.4142, "elevation": 2, "climate": "Marmara", "population": 540662},
            
            # İç Anadolu 
            "Ankara": {"lat": 39.9334, "lon": 32.8597, "elevation": 938, "climate": "İç Anadolu", "population": 5639076},
            "Konya": {"lat": 37.8667, "lon": 32.4833, "elevation": 1016, "climate": "İç Anadolu", "population": 2232374},
            "Kayseri": {"lat": 38.7205, "lon": 35.4826, "elevation": 1050, "climate": "İç Anadolu", "population": 1404276},
            "Sivas": {"lat": 39.7477, "lon": 37.0179, "elevation": 1285, "climate": "İç Anadolu", "population": 638956},
            "Yozgat": {"lat": 39.8181, "lon": 34.8147, "elevation": 800, "climate": "İç Anadolu", "population": 424981},
            "Çorum": {"lat": 40.5499, "lon": 34.9537, "elevation": 801, "climate": "İç Anadolu", "population": 527863},
            "Amasya": {"lat": 40.6539, "lon": 35.8336, "elevation": 400, "climate": "İç Anadolu", "population": 337508},
            "Tokat": {"lat": 40.3167, "lon": 36.5544, "elevation": 623, "climate": "İç Anadolu", "population": 602567},
            "Nevşehir": {"lat": 38.6244, "lon": 34.7236, "elevation": 1224, "climate": "İç Anadolu", "population": 303010},
            "Kırşehir": {"lat": 39.1458, "lon": 34.1606, "elevation": 985, "climate": "İç Anadolu", "population": 243042},
            "Aksaray": {"lat": 38.3726, "lon": 34.0254, "elevation": 980, "climate": "İç Anadolu", "population": 423011},
            "Niğde": {"lat": 37.9667, "lon": 34.6833, "elevation": 1229, "climate": "İç Anadolu", "population": 362861},
            "Kırıkkale": {"lat": 39.8468, "lon": 33.5153, "elevation": 746, "climate": "İç Anadolu", "population": 278749},
            "Çankırı": {"lat": 40.6013, "lon": 33.6134, "elevation": 800, "climate": "İç Anadolu", "population": 195789},
            "Karabük": {"lat": 41.2061, "lon": 32.6208, "elevation": 725, "climate": "İç Anadolu", "population": 248458},
            "Zonguldak": {"lat": 41.4564, "lon": 31.7987, "elevation": 135, "climate": "İç Anadolu", "population": 596053},
            "Bolu": {"lat": 40.7397, "lon": 31.6083, "elevation": 725, "climate": "İç Anadolu", "population": 311810},
            "Düzce": {"lat": 40.8438, "lon": 31.1565, "elevation": 135, "climate": "İç Anadolu", "population": 395679},
            "Kastamonu": {"lat": 41.3887, "lon": 33.7767, "elevation": 678, "climate": "İç Anadolu", "population": 376945},
            "Sinop": {"lat": 42.0231, "lon": 35.1531, "elevation": 0, "climate": "İç Anadolu", "population": 220799},
            
            # Doğu Anadolu 
            "Kars": {"lat": 40.6013, "lon": 43.0975, "elevation": 1768, "climate": "Doğu Anadolu", "population": 284923},
            "Erzurum": {"lat": 39.9055, "lon": 41.2658, "elevation": 1756, "climate": "Doğu Anadolu", "population": 762321},
            "Van": {"lat": 38.4891, "lon": 43.4089, "elevation": 1727, "climate": "Doğu Anadolu", "population": 1148637},
            "Ağrı": {"lat": 39.7191, "lon": 43.0503, "elevation": 1646, "climate": "Doğu Anadolu", "population": 536199},
            "Iğdır": {"lat": 39.9237, "lon": 44.0450, "elevation": 850, "climate": "Doğu Anadolu", "population": 199442},
            "Ardahan": {"lat": 41.1105, "lon": 42.7022, "elevation": 1067, "climate": "Doğu Anadolu", "population": 98335},
            "Erzincan": {"lat": 39.7500, "lon": 39.5000, "elevation": 1150, "climate": "Doğu Anadolu", "population": 234747},
            "Tunceli": {"lat": 39.1081, "lon": 39.5483, "elevation": 1727, "climate": "Doğu Anadolu", "population": 83443},
            "Bingöl": {"lat": 38.8856, "lon": 40.4989, "elevation": 1727, "climate": "Doğu Anadolu", "population": 281205},
            "Muş": {"lat": 38.9462, "lon": 41.7539, "elevation": 1727, "climate": "Doğu Anadolu", "population": 408809},
            "Bitlis": {"lat": 38.4011, "lon": 42.1078, "elevation": 1727, "climate": "Doğu Anadolu", "population": 350994},
            "Hakkari": {"lat": 37.5744, "lon": 43.7408, "elevation": 1727, "climate": "Doğu Anadolu", "population": 278775},
            "Şırnak": {"lat": 37.4187, "lon": 42.4918, "elevation": 1727, "climate": "Doğu Anadolu", "population": 537762},
            
            # Karadeniz 
            "Trabzon": {"lat": 41.0015, "lon": 39.7178, "elevation": 0, "climate": "Karadeniz", "population": 811901},
            "Rize": {"lat": 41.0201, "lon": 40.5234, "elevation": 5, "climate": "Karadeniz", "population": 344359},
            "Ordu": {"lat": 40.9839, "lon": 37.8764, "elevation": 5, "climate": "Karadeniz", "population": 761165},
            "Giresun": {"lat": 40.9128, "lon": 38.3895, "elevation": 5, "climate": "Karadeniz", "population": 448721},
            "Artvin": {"lat": 41.1828, "lon": 41.8183, "elevation": 5, "climate": "Karadeniz", "population": 168068},
            "Gümüşhane": {"lat": 40.4603, "lon": 39.4814, "elevation": 5, "climate": "Karadeniz", "population": 141702},
            "Bayburt": {"lat": 40.2567, "lon": 40.2249, "elevation": 5, "climate": "Karadeniz", "population": 78550},
            "Bartın": {"lat": 41.6358, "lon": 32.3375, "elevation": 5, "climate": "Karadeniz", "population": 198249},
            
            # Akdeniz 
            "Antalya": {"lat": 36.8969, "lon": 30.7133, "elevation": 30, "climate": "Akdeniz", "population": 2548308},
            "Mersin": {"lat": 36.8000, "lon": 34.6333, "elevation": 10, "climate": "Akdeniz", "population": 1854472},
            "Adana": {"lat": 37.0000, "lon": 35.3213, "elevation": 23, "climate": "Akdeniz", "population": 2258718},
            "Hatay": {"lat": 36.2021, "lon": 36.1600, "elevation": 89, "climate": "Akdeniz", "population": 1658400},
            "Kahramanmaraş": {"lat": 37.5858, "lon": 36.9228, "elevation": 518, "climate": "Akdeniz", "population": 1161634},
            "Osmaniye": {"lat": 37.0742, "lon": 36.2478, "elevation": 518, "climate": "Akdeniz", "population": 538759},
            "Burdur": {"lat": 37.7203, "lon": 30.2908, "elevation": 518, "climate": "Akdeniz", "population": 267092},
            "Isparta": {"lat": 37.7648, "lon": 30.5566, "elevation": 518, "climate": "Akdeniz", "population": 441412},
            
            # Güneydoğu Anadolu 
            "Diyarbakır": {"lat": 37.9144, "lon": 40.2306, "elevation": 660, "climate": "Güneydoğu Anadolu", "population": 1754247},
            "Mardin": {"lat": 37.3212, "lon": 40.7245, "elevation": 660, "climate": "Güneydoğu Anadolu", "population": 854716},
            "Batman": {"lat": 37.8812, "lon": 41.1351, "elevation": 540, "climate": "Güneydoğu Anadolu", "population": 620278},
            "Şanlıurfa": {"lat": 37.1674, "lon": 38.7955, "elevation": 518, "climate": "Güneydoğu Anadolu", "population": 2143020},
            "Gaziantep": {"lat": 37.0662, "lon": 37.3833, "elevation": 838, "climate": "Güneydoğu Anadolu", "population": 2130254},
            "Siirt": {"lat": 37.9274, "lon": 41.9456, "elevation": 660, "climate": "Güneydoğu Anadolu", "population": 331980},
            "Kilis": {"lat": 36.7184, "lon": 37.1212, "elevation": 660, "climate": "Güneydoğu Anadolu", "population": 142792},
            "Adıyaman": {"lat": 37.7648, "lon": 38.2786, "elevation": 660, "climate": "Güneydoğu Anadolu", "population": 632459},
            
            # Ege 
            "İzmir": {"lat": 38.4192, "lon": 27.1287, "elevation": 25, "climate": "Ege", "population": 4367251},
            "Manisa": {"lat": 38.6191, "lon": 27.4289, "elevation": 71, "climate": "Ege", "population": 1443426},
            "Aydın": {"lat": 37.8561, "lon": 27.8413, "elevation": 65, "climate": "Ege", "population": 1110972},
            "Muğla": {"lat": 37.2154, "lon": 28.3636, "elevation": 2, "climate": "Ege", "population": 1008567},
            "Denizli": {"lat": 37.7765, "lon": 29.0864, "elevation": 354, "climate": "Ege", "population": 1055562},
            "Afyonkarahisar": {"lat": 38.7500, "lon": 30.5500, "elevation": 1014, "climate": "Ege", "population": 736912},
            "Kütahya": {"lat": 39.4167, "lon": 29.9833, "elevation": 930, "climate": "Ege", "population": 576688},
            "Uşak": {"lat": 38.6742, "lon": 29.4058, "elevation": 750, "climate": "Ege", "population": 369433},
            "Bilecik": {"lat": 40.1506, "lon": 29.9792, "elevation": 850, "climate": "Ege", "population": 228334}
        }
    
    def generate_training_data(self) -> pd.DataFrame:
        """ML modelleri için eğitim verisi oluştur"""
        print("📊 Eğitim verisi oluşturuluyor...")
        
        training_data = []
        
        for city_name, city_data in self.cities_data.items():
            for year in range(2020, 2025):  # 5 yıllık veri
                for month in range(1, 13):
                    for day in range(1, 29):  # Her ayın 28 günü
                        # Coğrafi (enlem, boylam, yükseklik, iklim, nüfus)
                        lat = city_data["lat"]
                        lon = city_data["lon"]
                        elevation = city_data["elevation"]
                        climate = city_data["climate"]
                        population = city_data["population"]
                        
                        # Tarih yıl ay gün
                        date = datetime.datetime(year, month, day)
                        day_of_week = date.weekday()
                        day_of_year = date.timetuple().tm_yday
                        
                        # Mevsimsel (Ayların mevsimleri)
                        season = self._get_season(month)
                        
                        # Hava durumu tahmini (coğrafi ve mevsimsel kurallara göre)
                        weather, temp = self._predict_weather_rule_based(lat, lon, elevation, climate, month, day_of_year)
                        
                        # Nüfus etkili Trafik yoğunluğu tahmini
                        traffic_multiplier = self._predict_traffic_rule_based(city_name, day_of_week, month, population)
                        
                        # Eğitim verisi(Şehir, enlem, boylam, yükseklik, nüfus, iklim, ay, hafta, yıl, mevsim, hava durumu, sıcaklık, trafik yoğunluğu)
                        training_data.append({
                            'city': city_name,
                            'latitude': lat,
                            'longitude': lon,
                            'elevation': elevation,
                            'population': population,
                            'climate': climate,
                            'month': month,
                            'day_of_week': day_of_week,
                            'day_of_year': day_of_year,
                            'season': season,
                            'weather': weather,
                            'temperature': temp,
                            'traffic_multiplier': traffic_multiplier
                        })
        
        return pd.DataFrame(training_data)
    
    #Aya göre mevsim döndür
    def _get_season(self, month: int) -> str:
        """Ay numarasına göre mevsim döndür"""
        if month in [12, 1, 2]:
            return "kış"
        elif month in [3, 4, 5]:
            return "ilkbahar"
        elif month in [6, 7, 8]:
            return "yaz"
        else:
            return "sonbahar"
    
    def _predict_weather_rule_based(self, lat: float, lon: float, elevation: float, climate: str, month: int, day_of_year: int) -> Tuple[str, float]:
        """Kural tabanlı hava durumu tahmini"""
        # Temel sıcaklık hesaplama
        base_temp = 15 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Enlem etkisi (kuzeye gittikçe soğur)
        lat_effect = (lat - 40) * -0.5
        
        # Yükseklik etkisi (her 100m için 0.6°C soğur)
        elevation_effect = elevation * -0.006
        
        # İklim etkisi
        climate_effects = {
            "Akdeniz": 3, "Ege": 2, "Marmara": 0, "İç Anadolu": -2, 
            "Karadeniz": 1, "Doğu Anadolu": -5, "Güneydoğu Anadolu": 2
        }
        #İklim etkisi
        climate_effect = climate_effects.get(climate, 0)
        #Sıcaklık hesaplama
        temp = base_temp + lat_effect + elevation_effect + climate_effect
        
        # Hava durumu belirleme
        if climate == "Doğu Anadolu" and month in [12, 1, 2, 3]:
            weather = "kar"
        elif climate == "Karadeniz":
            weather = "yağmur" if np.random.random() > 0.3 else "güneş"
        elif climate == "Akdeniz" and month in [6, 7, 8, 9]:
            weather = "güneş"
        elif temp < 5 and month in [12, 1, 2]:
            weather = "kar"
        elif temp > 25 and month in [6, 7, 8]:
            weather = "güneş"
        elif month in [6, 7, 8]:  # Yaz ayları
            weather = "güneş" if np.random.random() > 0.2 else "yağmur"  # %80 güneş, %20 yağmur
        elif month in [12, 1, 2]:  # Kış ayları
            weather = "kar" if np.random.random() > 0.3 else "yağmur"  # %70 kar, %30 yağmur
        else:  # İlkbahar ve sonbahar
            weather = "yağmur" if np.random.random() > 0.4 else "güneş"  # %60 yağmur, %40 güneş
        
        return weather, round(temp, 1)
    
    def _predict_traffic_rule_based(self, city: str, day_of_week: int, month: int, population: int) -> float:
        """Kural tabanlı trafik yoğunluğu tahmini (tatil kontrolü HolidayService'e bırakıldı)"""
        base_multiplier = 1.0
        
        # Nüfus etkisi
        if population > 5000000:  # 5milyon nüfuslu şehirler
            base_multiplier *= 1.5
        elif population > 2000000:  # 2milyon nüfuslu şehirler
            base_multiplier *= 1.3
        elif population > 1000000:  # 1milyon nüfuslu şehirler
            base_multiplier *= 1.2
        
        # Hafta sonu etkisi (tatil kontrolü HolidayService'e bırakıldı)
        if day_of_week >= 5:  # Cumartesi, Pazar
            if city.lower() in ["antalya", "mersin", "adana", "muğla", "aydın", "izmir"]:
                base_multiplier *= 1.4  # Turizm şehirleri
            else:
                base_multiplier *= 0.7  # Diğer şehirler
        
        # Mevsim etkisi
        if month in [7, 8]:  # Yaz tatili
            if city.lower() in ["antalya", "mersin", "adana", "muğla", "aydın", "izmir"]:
                base_multiplier *= 1.6
            else:
                base_multiplier *= 0.8
        
        return round(base_multiplier, 2)
    
    def load_or_train_models(self):
        """Modelleri yükle veya eğit"""
        # Model dosyalarının yolları
        model_files = ["../models/weather_model.pkl", "../models/temperature_model.pkl", "../models/traffic_model.pkl", "../models/scaler.pkl", "../models/weather_encoder.pkl"]
        
        # Modelleri yükle
        if all(os.path.exists(f) for f in model_files):
            self.weather_model = joblib.load("../models/weather_model.pkl")
            self.temperature_model = joblib.load("../models/temperature_model.pkl")
            self.traffic_model = joblib.load("../models/traffic_model.pkl")
            self.scaler = joblib.load("../models/scaler.pkl")
            self.weather_encoder = joblib.load("../models/weather_encoder.pkl")
        else:
            print("🤖 Yeni modeller eğitiliyor...")
            self.train_models()
    
    def train_models(self):
        """ML modellerini eğit"""
        # Eğitim verisi oluştur
        df = self.generate_training_data()
        
        # Özellikler ve hedefler
        features = ['latitude', 'longitude', 'elevation', 'population', 'month', 'day_of_week', 'day_of_year']
        X = df[features].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Hava durumu modeli (çok küçük model) Classifier modeli yapıldı (Kategorik değerler için)
        weather_encoded = self.weather_encoder.fit_transform(df['weather'])
        self.weather_model = RandomForestClassifier(n_estimators=10, max_depth=5, min_samples_split=50, random_state=42)
        self.weather_model.fit(X_scaled, weather_encoded)
        
        # Sıcaklık modeli (çok küçük model) Regressor modeli yapıldı (Sayısal değerler için)
        self.temperature_model = RandomForestRegressor(n_estimators=10, max_depth=5, min_samples_split=50, random_state=42)
        self.temperature_model.fit(X_scaled, df['temperature'])
        
        # Trafik modeli (çok küçük model) Regressor modeli yapıldı (Sayısal değerler için)
        self.traffic_model = RandomForestRegressor(n_estimators=10, max_depth=5, min_samples_split=50, random_state=42)
        self.traffic_model.fit(X_scaled, df['traffic_multiplier'])
        
        # Modelleri kaydet
        joblib.dump(self.weather_model, "../models/weather_model.pkl")
        joblib.dump(self.temperature_model, "../models/temperature_model.pkl")
        joblib.dump(self.traffic_model, "../models/traffic_model.pkl")
        joblib.dump(self.scaler, "../models/scaler.pkl")
        joblib.dump(self.weather_encoder, "../models/weather_encoder.pkl")
        
        print("✅ Modeller eğitildi ve kaydedildi")
    
    def get_weather_prediction(self, city: str, month: int) -> Dict:
        """ML tabanlı hava durumu tahmini (kural tabanlı ile birleştirilmiş)"""
        city_normalized = city.title()
        if city_normalized not in self.cities_data:
            return self._get_default_weather(city, month)
        
        city_data = self.cities_data[city_normalized]
        
        # Kural tabanlı tahmin (güvenilir)
        rule_based_weather, rule_based_temp = self._predict_weather_rule_based(
            city_data["lat"], city_data["lon"], city_data["elevation"], 
            city_data["climate"], month, month * 30
        )
        
        # ML tabanlı tahmin
        features = np.array([[
            city_data["lat"],
            city_data["lon"],
            city_data["elevation"],
            city_data["population"],
            month,
            0,  # Varsayılan gün (Pazartesi)
            month * 30  # Yaklaşık gün numarası
        ]])
        #Özellikleri ölçeklendir
        features_scaled = self.scaler.transform(features)
        #Hava durumu modeli
        weather_encoded = self.weather_model.predict(features_scaled)[0]
        #Hava durumu kodu
        ml_weather = self.weather_encoder.inverse_transform([weather_encoded])[0]
        #Sıcaklık modeli
        ml_temperature = self.temperature_model.predict(features_scaled)[0]
        
        # Öncelik kural tabanlı tahmine ver (özellikle Doğu Anadolu için)
        if city_data["climate"] == "Doğu Anadolu" and month in [12, 1, 2, 3]:
            final_weather = rule_based_weather
            final_temp = rule_based_temp 
            confidence = 0.95 #Güvenilirlik
            explanation = f"Kural tabanlı tahmin: {city} şehri {month}. ayında {rule_based_weather} hava durumu bekleniyor (Doğu Anadolu kış koşulları)" 
        else:
            # ML ve kural tabanlı tahminleri birleştir
            if rule_based_weather == ml_weather:
                final_weather = ml_weather
                final_temp = (rule_based_temp + ml_temperature) / 2
                confidence = 0.90
                explanation = f"ML ve kural tabanlı tahminler uyumlu: {city} şehri {month}. ayında {ml_weather} hava durumu"
            else:
                # Çelişki varsa kural tabanlı tahmini tercih et
                final_weather = rule_based_weather
                final_temp = rule_based_temp
                confidence = 0.85
                explanation = f"Kural tabanlı tahmin tercih edildi: {city} şehri {month}. ayında {rule_based_weather} hava durumu (ML: {ml_weather})"
        
        return {
            "city": city,
            "month": month,
            "predicted_weather": final_weather,
            "confidence": confidence,
            "avg_temperature": round(final_temp, 1),
            "climate_zone": city_data["climate"],
            "explanation": explanation
        }
    #Bilinmeyen şehirler için varsayılan tahmin
    def _get_default_weather(self, city: str, month: int) -> Dict:
        """Bilinmeyen şehirler için varsayılan tahmin"""
        return {
            "city": city,
            "month": month,
            "predicted_weather": "güneş",
            "confidence": 0.6,
            "avg_temperature": 20,
            "climate_zone": "Bilinmiyor",
            "explanation": f"{city} şehri için varsayılan tahmin"
        }
    # Tatil kontrolü artık HolidayService tarafından yapılıyor
    # Bu metod kaldırıldı - HolidayService kullanın
    
    def calculate_traffic_multiplier(self, city: str, date_str: str) -> float:
        """ML tabanlı trafik yoğunluğu tahmini (tatil kontrolü HolidayService'e bırakıldı)"""
        city_normalized = city.title()
        if city_normalized not in self.cities_data:
            return 1.0
        
        try:
            #Tarih formatını kontrol et
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            city_data = self.cities_data[city_normalized]
            
            # Özellik vektörü
            features = np.array([[
                city_data["lat"],
                city_data["lon"],
                city_data["elevation"],
                city_data["population"],
                date_obj.month,
                date_obj.weekday(), 
                date_obj.timetuple().tm_yday 
            ]])
            
            features_scaled = self.scaler.transform(features) #Özellikleri ölçeklendir
            multiplier = self.traffic_model.predict(features_scaled)[0] #Trafik modeli
            
            # Tatil etkisi artık HolidayService tarafından hesaplanıyor
            # Burada sadece coğrafi ve mevsimsel etkileri hesaplıyoruz
            
            return round(multiplier, 2)
            
        except:
            return 1.0
    
    def calculate_toll_cost(self, route_distance: float, route_highways: List[str]) -> Dict:
        """Rota ücreti hesaplama (basitleştirilmiş)"""
        total_cost = 0
        toll_details = []
        
        # Basit ücret hesaplama
        for highway in route_highways:
            if "köprü" in highway.lower() or "bridge" in highway.lower():
                cost = 200
                total_cost += cost
                toll_details.append({
                    "name": highway,
                    "cost": cost,
                    "type": "köprü"
                })
            elif "otoyol" in highway.lower() or "highway" in highway.lower():
                cost = route_distance * 0.15
                total_cost += cost
                toll_details.append({
                    "name": highway,
                    "cost": round(cost, 2),
                    "type": "otoyol"
                })
        
        return {
            "total_cost": round(total_cost, 2),
            "toll_details": toll_details,
            "cost_per_km": round(total_cost / route_distance, 2) if route_distance > 0 else 0
        }

# Test fonksiyonu
if __name__ == "__main__":
    db = MLWeatherDatabase()
    
    print("=== ML Tabanlı Hava Durumu Tahminleri ===")
    cities = ["İstanbul", "Kars", "Trabzon", "Antalya", "Diyarbakır", "Ankara"]
    for city in cities:
        for month in [1, 7]:  # Ocak ve Temmuz
            pred = db.get_weather_prediction(city, month)
            print(f"{city} - {month}. ay: {pred['predicted_weather']} ({pred['avg_temperature']}°C, güven: %{pred['confidence']*100:.0f})")
    
    print("\n=== ML Tabanlı Trafik Tahminleri ===")
    for city in cities:
        multiplier = db.calculate_traffic_multiplier(city, "2024-07-15", False)
        print(f"{city} - Trafik çarpanı: {multiplier}") 