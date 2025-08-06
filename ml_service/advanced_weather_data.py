
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
import requests
import sqlite3
from datetime import datetime, timedelta

#ML hava durumu veritabanı sınıfı
class MLWeatherDatabase:
    def __init__(self):
        self.weather_model = None #Hava durumu modeli
        self.temperature_model = None #Sıcaklık modeli
        self.traffic_model = None #Trafik modeli
        self.scaler = StandardScaler() #Ölçekleyici
        self.weather_encoder = LabelEncoder() #Hava durumu kodlayıcı
        
        # Türkiye şehirleri coğrafi verileri
        self.cities_data = self._load_cities_geographic_data()
        
        # Tarihsel veri veritabanı
        self.db_path = "historical_weather.db"
        self._init_database()
        
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
    
    def _init_database(self):
        """Tarihsel veri veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hava durumu verileri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                date TEXT NOT NULL,
                weather_condition TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL,
                wind_speed REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, date)
            )
        ''')
        
        # Şehir istatistikleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS city_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                avg_temperature REAL,
                avg_humidity REAL,
                avg_wind_speed REAL,
                weather_probabilities TEXT,
                sample_count INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, month, day)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_historical_data(self, city: str, start_date: str, end_date: str):
        """Belirli bir şehir için tarihsel veri topla"""
        try:
            # OpenWeatherMap API'den veri al (ücretsiz plan)
            from dotenv import load_dotenv
            import os
            load_dotenv()
            api_key = os.getenv("OPENWEATHER_API_KEY")
            
            if not api_key:
                raise ValueError("OPENWEATHER_API_KEY .env dosyasında bulunamadı!")
                
            base_url = "http://api.openweathermap.org/data/2.5/weather"
            
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_date = start
            while current_date <= end:
                # Unix timestamp
                timestamp = int(current_date.timestamp())
                
                # API çağrısı
                params = {
                    'q': f"{city},TR",
                    'appid': api_key,
                    'units': 'metric',
                    'dt': timestamp
                }
                
                response = requests.get(base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    weather_condition = data['weather'][0]['main'].lower()
                    temperature = data['main']['temp']
                    humidity = data['main']['humidity']
                    wind_speed = data['wind']['speed']
                    
                    # Veritabanına kaydet
                    cursor.execute('''
                        INSERT OR REPLACE INTO weather_data 
                        (city, date, weather_condition, temperature, humidity, wind_speed)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (city, current_date.strftime("%Y-%m-%d"), weather_condition, 
                          temperature, humidity, wind_speed))
                
                current_date += timedelta(days=1)
            
            conn.commit()
            conn.close()
            print(f"✅ {city} için tarihsel veri toplandı: {start_date} - {end_date}")
            
        except Exception as e:
            print(f"❌ {city} için veri toplama hatası: {e}")
    
    def get_historical_average(self, city: str, month: int, day: int) -> Dict:
        """Belirli bir gün için son 3 yıllık ortalama verileri al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Son 3 yılın aynı günü için verileri al
            current_year = datetime.now().year
            years = [current_year - 3, current_year - 2, current_year - 1]
            
            temperatures = []
            humidities = []
            wind_speeds = []
            weather_conditions = []
            
            for year in years:
                date_str = f"{year}-{month:02d}-{day:02d}"
                cursor.execute('''
                    SELECT temperature, humidity, wind_speed, weather_condition
                    FROM weather_data 
                    WHERE city = ? AND date = ?
                ''', (city, date_str))
                
                result = cursor.fetchone()
                if result:
                    temperatures.append(result[0])
                    humidities.append(result[1])
                    wind_speeds.append(result[2])
                    weather_conditions.append(result[3])
            
            conn.close()
            
            if temperatures:
                # Hava durumu olasılıklarını hesapla
                weather_counts = {}
                for condition in weather_conditions:
                    weather_counts[condition] = weather_counts.get(condition, 0) + 1
                
                total_samples = len(weather_conditions)
                weather_probabilities = {
                    condition: count / total_samples 
                    for condition, count in weather_counts.items()
                }
                
                # En olası hava durumu
                most_likely_weather = max(weather_probabilities, key=weather_probabilities.get)
                
                return {
                    'avg_temperature': np.mean(temperatures),
                    'avg_humidity': np.mean(humidities),
                    'avg_wind_speed': np.mean(wind_speeds),
                    'weather_probabilities': weather_probabilities,
                    'most_likely_weather': most_likely_weather,
                    'confidence': weather_probabilities[most_likely_weather],
                    'sample_count': total_samples
                }
            else:
                # Veri yoksa boş döndür - fallback yok
                return {
                    'avg_temperature': 0.0,
                    'avg_humidity': 0.0,
                    'avg_wind_speed': 0.0,
                    'weather_probabilities': {},
                    'most_likely_weather': 'veri_yok',
                    'confidence': 0.0,
                    'sample_count': 0
                }
                
        except Exception as e:
            print(f"❌ {city} için tarihsel ortalama hatası: {e}")
            return {
                'avg_temperature': 0.0,
                'avg_humidity': 0.0,
                'avg_wind_speed': 0.0,
                'weather_probabilities': {},
                'most_likely_weather': 'veri_yok',
                'confidence': 0.0,
                'sample_count': 0
            }
    
    def _get_rule_based_fallback(self, city: str, month: int, day: int) -> Dict:
        """Veri yoksa kural tabanlı fallback"""
        city_data = self.cities_data.get(city.title(), {})
        if not city_data:
            return {
                'avg_temperature': 15.0,
                'avg_humidity': 60.0,
                'avg_wind_speed': 10.0,
                'weather_probabilities': {'güneş': 0.6, 'yağmur': 0.3, 'kar': 0.1},
                'most_likely_weather': 'güneş',
                'confidence': 0.6,
                'sample_count': 0
            }
        
        # Basit kural tabanlı tahmin
        if month in [12, 1, 2]:  # Kış
            if city_data['climate'] == 'Doğu Anadolu':
                weather = 'kar'
                temp = -5.0
            else:
                weather = 'yağmur'
                temp = 5.0
        elif month in [6, 7, 8]:  # Yaz
            weather = 'güneş'
            temp = 25.0
        else:  # İlkbahar/Sonbahar
            weather = 'güneş'
            temp = 15.0
        
        return {
            'avg_temperature': temp,
            'avg_humidity': 60.0,
            'avg_wind_speed': 10.0,
            'weather_probabilities': {weather: 0.8},
            'most_likely_weather': weather,
            'confidence': 0.8,
            'sample_count': 0
        }
    
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
    
    def get_weather_prediction(self, city: str, month: int, day: int = None) -> Dict:
        """Tarihsel veri tabanlı hava durumu tahmini - SADECE GERÇEK VERİ VARSA"""
        city_normalized = city.title()
        if city_normalized not in self.cities_data:
            return {
                "city": city,
                "month": month,
                "predicted_weather": "veri_yok",
                "confidence": 0.0,
                "avg_temperature": 0.0,
                "climate_zone": "Bilinmiyor",
                "explanation": f"{city} şehri için tarihsel veri bulunamadı"
            }
        
        # Gün belirtilmemişse ayın ortası (15. gün) kullan
        if day is None:
            day = 15
        
        # Tarihsel ortalama verileri al
        historical_data = self.get_historical_average(city_normalized, month, day)
        
        # Eğer gerçek tarihsel veri yoksa (sample_count = 0), tahmin yapma
        if historical_data['sample_count'] == 0:
            return {
                "city": city,
                "month": month,
                "day": day,
                "predicted_weather": "veri_yok",
                "confidence": 0.0,
                "avg_temperature": 0.0,
                "avg_humidity": 0.0,
                "avg_wind_speed": 0.0,
                "climate_zone": self.cities_data[city_normalized]["climate"],
                "weather_probabilities": {},
                "sample_count": 0,
                "explanation": f"{city} şehri için {month}. ayının {day}. gününde son 3 yılda gerçek hava durumu verisi bulunamadı"
            }
        
        city_data = self.cities_data[city_normalized]
        
        return {
            "city": city,
            "month": month,
            "day": day,
            "predicted_weather": historical_data['most_likely_weather'],
            "confidence": historical_data['confidence'],
            "avg_temperature": round(historical_data['avg_temperature'], 1),
            "avg_humidity": round(historical_data['avg_humidity'], 1),
            "avg_wind_speed": round(historical_data['avg_wind_speed'], 1),
            "climate_zone": city_data["climate"],
            "weather_probabilities": historical_data['weather_probabilities'],
            "sample_count": historical_data['sample_count'],
            "explanation": f"SON 3 YILIN GERÇEK VERİSİ: {city} şehri {month}. ayının {day}. günü için son {historical_data['sample_count']} yılın gerçek hava durumu ortalaması"
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
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
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

    def collect_all_cities_data(self, start_date: str, end_date: str):
        """Tüm Türkiye şehirleri için tarihsel veri topla"""
        print(f"📊 Tüm şehirler için tarihsel veri toplanıyor: {start_date} - {end_date}")
        
        total_cities = len(self.cities_data)
        current = 0
        
        for city_name in self.cities_data.keys():
            current += 1
            print(f"🔄 [{current}/{total_cities}] {city_name} için veri toplanıyor...")
            
            try:
                self.collect_historical_data(city_name, start_date, end_date)
                
                # API limit aşımını önlemek için bekle
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ {city_name} için veri toplama hatası: {e}")
                continue
        
        print("✅ Tüm şehirler için tarihsel veri toplama tamamlandı!")
    
    def update_city_statistics(self):
        """Şehir istatistiklerini güncelle"""
        print("📈 Şehir istatistikleri güncelleniyor...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for city_name in self.cities_data.keys():
            print(f"🔄 {city_name} istatistikleri hesaplanıyor...")
            
            # Her gün için istatistik hesapla
            for month in range(1, 13):
                for day in range(1, 29):  # Her ayın 28 günü
                    historical_data = self.get_historical_average(city_name, month, day)
                    
                    # İstatistikleri veritabanına kaydet
                    weather_probs_json = json.dumps(historical_data['weather_probabilities'])
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO city_statistics 
                        (city, month, day, avg_temperature, avg_humidity, avg_wind_speed, 
                         weather_probabilities, sample_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (city_name, month, day, historical_data['avg_temperature'],
                          historical_data['avg_humidity'], historical_data['avg_wind_speed'],
                          weather_probs_json, historical_data['sample_count']))
        
        conn.commit()
        conn.close()
        print("✅ Şehir istatistikleri güncellendi!")
    
    def get_city_statistics(self, city: str, month: int, day: int) -> Dict:
        """Veritabanından şehir istatistiklerini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT avg_temperature, avg_humidity, avg_wind_speed, 
                       weather_probabilities, sample_count
                FROM city_statistics 
                WHERE city = ? AND month = ? AND day = ?
            ''', (city, month, day))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                weather_probabilities = json.loads(result[3])
                most_likely_weather = max(weather_probabilities, key=weather_probabilities.get)
                
                return {
                    'avg_temperature': result[0],
                    'avg_humidity': result[1],
                    'avg_wind_speed': result[2],
                    'weather_probabilities': weather_probabilities,
                    'most_likely_weather': most_likely_weather,
                    'confidence': weather_probabilities[most_likely_weather],
                    'sample_count': result[4]
                }
            else:
                # Veritabanında yoksa hesapla
                return self.get_historical_average(city, month, day)
                
        except Exception as e:
            print(f"❌ {city} istatistik hatası: {e}")
            return self.get_historical_average(city, month, day)

# Test fonksiyonu
if __name__ == "__main__":
    db = MLWeatherDatabase()
    
    print("=== Tarihsel Veri Tabanlı Hava Durumu Tahminleri ===")
    
    # Test şehirleri
    test_cities = ["İstanbul", "Kars", "Trabzon", "Antalya", "Diyarbakır", "Ankara", "Iğdır"]
    test_dates = [
        (12, 12),  # Aralık 12 (Kars-Iğdır testi)
        (7, 15),   # Temmuz 15
        (1, 1),    # Ocak 1
        (3, 21)    # Mart 21
    ]
    
    for city in test_cities:
        print(f"\n🌤️ {city} şehri tahminleri:")
        for month, day in test_dates:
            pred = db.get_weather_prediction(city, month, day)
            print(f"  {month:02d}/{day:02d}: {pred['predicted_weather']} ({pred['avg_temperature']}°C, nem: %{pred['avg_humidity']:.0f}, güven: %{pred['confidence']*100:.0f})")
            print(f"    Örnek sayısı: {pred['sample_count']}")
            print(f"    Olasılıklar: {pred['weather_probabilities']}")
    
    print("\n=== Veri Toplama Örneği ===")
    print("Tüm şehirler için veri toplamak için:")
    print("db.collect_all_cities_data('2021-01-01', '2024-12-31')")
    print("db.update_city_statistics()")
    
    print("\n=== Tek Şehir Testi ===")
    # Iğdır için özel test
    igdir_pred = db.get_weather_prediction("Iğdır", 12, 12)
    print(f"Iğdır - 12 Aralık: {igdir_pred['predicted_weather']} ({igdir_pred['avg_temperature']}°C)")
    print(f"Güven: %{igdir_pred['confidence']*100:.0f}, Örnek: {igdir_pred['sample_count']}") 