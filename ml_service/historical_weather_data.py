"""
Gerçek Tarihsel Hava Durumu Verileri Toplama ve İşleme Sistemi

Bu modül, Türkiye şehirleri için son 5 yıllık gerçek hava durumu verilerini toplar
ve gün bazında olasılık hesaplamaları yapar.

Özellikler:
- OpenWeatherMap API'den tarihsel veri çekme
- SQL Server LocalDB ile veri saklama
- Gün bazında olasılık hesaplamaları
- ML modelleri için eğitim verisi hazırlama
- Gerçek zamanlı tahmin için veri tabanı
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple, Optional
import time
from collections import defaultdict
import pyodbc
import urllib.parse

class HistoricalWeatherDataCollector:
    def __init__(self, api_key: str = "0d97a7dabc935b1c450dbe82a3234617"):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/onecall/timemachine"
        self.connection_string = self._get_connection_string()
        self.cities_data = self._load_cities_data()
        
        # Veritabanını oluştur
        self._create_database()
        
    def _get_connection_string(self) -> str:
        """SQL Server bağlantı string'i oluştur"""
        # LocalDB'yi öncelikle dene
        try:
            test_conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=master;Trusted_Connection=yes;', timeout=5)
            test_conn.close()
            print("✅ SQL Server LocalDB bağlantısı başarılı")
            return 'Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=HistoricalWeatherDB;Trusted_Connection=yes;'
        except Exception as e:
            print(f"⚠️ SQL Server LocalDB bağlantısı başarısız: {e}")
            
            # Normal SQL Server'ı dene
            try:
                test_conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;', timeout=5)
                test_conn.close()
                print("✅ SQL Server bağlantısı başarılı")
                return 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=HistoricalWeatherDB;Trusted_Connection=yes;'
            except Exception as e2:
                print(f"⚠️ SQL Server bağlantısı da başarısız: {e2}")
                print("⚠️ SQLite kullanılıyor...")
                return "sqlite:///historical_weather.db"
    
    def _load_cities_data(self) -> Dict:
        """Türkiye şehirlerinin koordinat verileri"""
        return {
            "İstanbul": {"lat": 41.0082, "lon": 28.9784},
            "Ankara": {"lat": 39.9334, "lon": 32.8597},
            "İzmir": {"lat": 38.4192, "lon": 27.1287},
            "Bursa": {"lat": 40.1885, "lon": 29.0610},
            "Antalya": {"lat": 36.8969, "lon": 30.7133},
            "Adana": {"lat": 37.0000, "lon": 35.3213},
            "Konya": {"lat": 37.8667, "lon": 32.4833},
            "Gaziantep": {"lat": 37.0662, "lon": 37.3833},
            "Kayseri": {"lat": 38.7205, "lon": 35.4826},
            "Mersin": {"lat": 36.8000, "lon": 34.6333},
            "Diyarbakır": {"lat": 37.9144, "lon": 40.2306},
            "Samsun": {"lat": 41.2867, "lon": 36.3300},
            "Denizli": {"lat": 37.7765, "lon": 29.0864},
            "Eskişehir": {"lat": 39.7767, "lon": 30.5206},
            "Trabzon": {"lat": 41.0015, "lon": 39.7178},
            "Erzurum": {"lat": 39.9055, "lon": 41.2658},
            "Van": {"lat": 38.4891, "lon": 43.4089},
            "Sivas": {"lat": 39.7477, "lon": 37.0179},
            "Malatya": {"lat": 38.3552, "lon": 38.3095},
            "Manisa": {"lat": 38.6191, "lon": 27.4289},
            "Kocaeli": {"lat": 40.8533, "lon": 29.8815},
            "Sakarya": {"lat": 40.7569, "lon": 30.3781},
            "Balıkesir": {"lat": 39.6484, "lon": 27.8826},
            "Kahramanmaraş": {"lat": 37.5858, "lon": 36.9371},
            "Aydın": {"lat": 37.8560, "lon": 27.8416},
            "Tekirdağ": {"lat": 40.9780, "lon": 27.5110},
            "Muğla": {"lat": 37.2154, "lon": 28.3636},
            "Elazığ": {"lat": 38.6810, "lon": 39.2264},
            "Afyonkarahisar": {"lat": 38.7507, "lon": 30.5567},
            "Tokat": {"lat": 40.3167, "lon": 36.5544},
            "Ordu": {"lat": 40.9839, "lon": 37.8764},
            "Çorum": {"lat": 40.5499, "lon": 34.9537},
            "Giresun": {"lat": 40.9128, "lon": 38.3895},
            "Rize": {"lat": 41.0201, "lon": 40.5234},
            "Kırıkkale": {"lat": 39.8468, "lon": 33.5153},
            "Aksaray": {"lat": 38.3726, "lon": 34.0254},
            "Nevşehir": {"lat": 38.6244, "lon": 34.7236},
            "Niğde": {"lat": 37.9667, "lon": 34.6833},
            "Kırşehir": {"lat": 39.1458, "lon": 34.1606},
            "Yozgat": {"lat": 39.8181, "lon": 34.8147},
            "Amasya": {"lat": 40.6539, "lon": 35.8336},
            "Çankırı": {"lat": 40.6013, "lon": 33.6134},
            "Karabük": {"lat": 41.2061, "lon": 32.6208},
            "Zonguldak": {"lat": 41.4564, "lon": 31.7987},
            "Bolu": {"lat": 40.7397, "lon": 31.6083},
            "Düzce": {"lat": 40.8438, "lon": 31.1565},
            "Kastamonu": {"lat": 41.3887, "lon": 33.7767},
            "Sinop": {"lat": 42.0231, "lon": 35.1531},
            "Kars": {"lat": 40.6013, "lon": 43.0975},
            "Ağrı": {"lat": 39.7191, "lon": 43.0503},
            "Iğdır": {"lat": 39.9237, "lon": 44.0450},
            "Ardahan": {"lat": 41.1105, "lon": 42.7022},
            "Erzincan": {"lat": 39.7500, "lon": 39.5000},
            "Tunceli": {"lat": 39.1081, "lon": 39.5483},
            "Bingöl": {"lat": 38.8856, "lon": 40.4989},
            "Muş": {"lat": 38.9462, "lon": 41.7539},
            "Bitlis": {"lat": 38.4011, "lon": 42.1078},
            "Hakkari": {"lat": 37.5744, "lon": 43.7408},
            "Şırnak": {"lat": 37.4187, "lon": 42.4918}
        }
    
    def _create_database(self):
        """SQL Server veritabanını oluştur"""
        try:
            # Önce normal SQL Server'ı dene
            try:
                master_conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;')
                cursor = master_conn.cursor()
                
                # Veritabanını oluştur (transaction dışında)
                cursor.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HistoricalWeatherDB') BEGIN CREATE DATABASE HistoricalWeatherDB END")
                master_conn.commit()
                master_conn.close()
                print("✅ SQL Server veritabanı oluşturuldu")
                
            except Exception as e:
                print(f"⚠️ SQL Server bağlantısı başarısız: {e}")
                # LocalDB'yi dene
                master_conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\\MSSQLLocalDB;Database=master;Trusted_Connection=yes;')
                cursor = master_conn.cursor()
                
                # Veritabanını oluştur (transaction dışında)
                cursor.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HistoricalWeatherDB') BEGIN CREATE DATABASE HistoricalWeatherDB END")
                master_conn.commit()
                master_conn.close()
                print("✅ SQL Server LocalDB veritabanı oluşturuldu")
            
            # Veritabanına bağlan
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Tarihsel hava durumu verileri tablosu
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='historical_weather' AND xtype='U')
                CREATE TABLE historical_weather (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    city NVARCHAR(100) NOT NULL,
                    date NVARCHAR(10) NOT NULL,
                    weather_main NVARCHAR(50) NOT NULL,
                    weather_description NVARCHAR(200),
                    temperature FLOAT,
                    humidity INT,
                    wind_speed FLOAT,
                    created_at DATETIME DEFAULT GETDATE(),
                    CONSTRAINT UQ_city_date UNIQUE(city, date)
                )
            ''')
            
            # Günlük olasılık hesaplamaları tablosu
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='daily_probabilities' AND xtype='U')
                CREATE TABLE daily_probabilities (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    city NVARCHAR(100) NOT NULL,
                    month INT NOT NULL,
                    day INT NOT NULL,
                    weather_main NVARCHAR(50) NOT NULL,
                    probability FLOAT NOT NULL,
                    sample_count INT NOT NULL,
                    last_updated DATETIME DEFAULT GETDATE(),
                    CONSTRAINT UQ_city_month_day_weather UNIQUE(city, month, day, weather_main)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ SQL Server LocalDB veritabanı oluşturuldu")
            
        except Exception as e:
            print(f"❌ Veritabanı oluşturma hatası: {e}")
            print("⚠️ SQLite'a fallback yapılıyor...")
            self._create_sqlite_database()
    
    def _create_sqlite_database(self):
        """SQLite veritabanını oluştur (fallback)"""
        import sqlite3
        
        conn = sqlite3.connect("historical_weather.db")
        cursor = conn.cursor()
        
        # Tarihsel hava durumu verileri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                date TEXT NOT NULL,
                weather_main TEXT NOT NULL,
                weather_description TEXT,
                temperature REAL,
                humidity INTEGER,
                wind_speed REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, date)
            )
        ''')
        
        # Günlük olasılık hesaplamaları tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_probabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                weather_main TEXT NOT NULL,
                probability REAL NOT NULL,
                sample_count INTEGER NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, month, day, weather_main)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ SQLite veritabanı oluşturuldu (fallback)")
    
    def _get_connection(self):
        """Veritabanı bağlantısı al"""
        try:
            if "sqlite" in self.connection_string:
                import sqlite3
                return sqlite3.connect("historical_weather.db")
            else:
                return pyodbc.connect(self.connection_string)
        except Exception as e:
            print(f"❌ Veritabanı bağlantı hatası: {e}")
            # SQLite'a fallback
            import sqlite3
            return sqlite3.connect("historical_weather.db")
    
    def collect_historical_data(self, start_year: int = 2020, end_year: int = 2024):
        """Son 5 yıllık tarihsel verileri topla"""
        print(f"📊 {start_year}-{end_year} arası tarihsel hava durumu verileri toplanıyor...")
        
        for city, coords in self.cities_data.items():
            print(f"🌤️ {city} için veriler toplanıyor...")
            
            # Her gün için veri topla
            current_date = datetime(start_year, 1, 1)
            end_date = datetime(end_year, 12, 31)
            
            while current_date <= end_date:
                try:
                    # OpenWeatherMap API'den tarihsel veri al
                    timestamp = int(current_date.timestamp())
                    url = f"{self.base_url}?lat={coords['lat']}&lon={coords['lon']}&dt={timestamp}&appid={self.api_key}&units=metric"
                    
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'data' in data and len(data['data']) > 0:
                            daily_data = data['data'][0]
                            
                            # Veritabanına kaydet
                            self._save_weather_data(
                                city=city,
                                date=current_date.strftime('%Y-%m-%d'),
                                weather_main=daily_data['weather'][0]['main'],
                                weather_description=daily_data['weather'][0]['description'],
                                temperature=daily_data['temp'],
                                humidity=daily_data['humidity'],
                                wind_speed=daily_data['wind_speed']
                            )
                    
                    # API rate limit için bekle
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"❌ {city} {current_date.strftime('%Y-%m-%d')} verisi alınamadı: {e}")
                
                current_date += timedelta(days=1)
            
            print(f"✅ {city} verileri tamamlandı")
        
        # Olasılık hesaplamalarını güncelle
        self._calculate_daily_probabilities()
        print("🎯 Günlük olasılık hesaplamaları tamamlandı")
    
    def _save_weather_data(self, city: str, date: str, weather_main: str, 
                          weather_description: str, temperature: float, 
                          humidity: int, wind_speed: float):
        """Hava durumu verisini veritabanına kaydet"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if "sqlite" in self.connection_string:
                cursor.execute('''
                    INSERT OR REPLACE INTO historical_weather 
                    (city, date, weather_main, weather_description, temperature, humidity, wind_speed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (city, date, weather_main, weather_description, temperature, humidity, wind_speed))
            else:
                cursor.execute('''
                    MERGE historical_weather AS target
                    USING (SELECT ? as city, ? as date, ? as weather_main, ? as weather_description, ? as temperature, ? as humidity, ? as wind_speed) AS source
                    ON target.city = source.city AND target.date = source.date
                    WHEN MATCHED THEN
                        UPDATE SET weather_main = source.weather_main, weather_description = source.weather_description, 
                                 temperature = source.temperature, humidity = source.humidity, wind_speed = source.wind_speed
                    WHEN NOT MATCHED THEN
                        INSERT (city, date, weather_main, weather_description, temperature, humidity, wind_speed)
                        VALUES (source.city, source.date, source.weather_main, source.weather_description, 
                                source.temperature, source.humidity, source.wind_speed);
                ''', (city, date, weather_main, weather_description, temperature, humidity, wind_speed))
            
            conn.commit()
        except Exception as e:
            print(f"❌ Veri kaydetme hatası: {e}")
        finally:
            conn.close()
    
    def _calculate_daily_probabilities(self):
        """Günlük hava durumu olasılıklarını hesapla"""
        conn = self._get_connection()
        
        # Her şehir için günlük olasılıkları hesapla
        for city in self.cities_data.keys():
            if "sqlite" in self.connection_string:
                query = '''
                    SELECT 
                        CAST(SUBSTR(date, 6, 2) AS INTEGER) as month,
                        CAST(SUBSTR(date, 9, 2) AS INTEGER) as day,
                        weather_main,
                        COUNT(*) as count
                    FROM historical_weather 
                    WHERE city = ?
                    GROUP BY month, day, weather_main
                    ORDER BY month, day, weather_main
                '''
            else:
                query = '''
                    SELECT 
                        CAST(SUBSTRING(date, 6, 2) AS INT) as month,
                        CAST(SUBSTRING(date, 9, 2) AS INT) as day,
                        weather_main,
                        COUNT(*) as count
                    FROM historical_weather 
                    WHERE city = ?
                    GROUP BY month, day, weather_main
                    ORDER BY month, day, weather_main
                '''
            
            df = pd.read_sql_query(query, conn, params=(city,))
            
            if not df.empty:
                # Her gün için toplam sayıyı hesapla
                daily_totals = df.groupby(['month', 'day'])['count'].sum().reset_index()
                daily_totals = daily_totals.rename(columns={'count': 'total_count'})
                
                # Olasılıkları hesapla
                df = df.merge(daily_totals, on=['month', 'day'])
                df['probability'] = df['count'] / df['total_count']
                
                # Veritabanına kaydet
                cursor = conn.cursor()
                for _, row in df.iterrows():
                    if "sqlite" in self.connection_string:
                        cursor.execute('''
                            INSERT OR REPLACE INTO daily_probabilities 
                            (city, month, day, weather_main, probability, sample_count)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (city, row['month'], row['day'], row['weather_main'], 
                             row['probability'], row['count']))
                    else:
                        cursor.execute('''
                            MERGE daily_probabilities AS target
                            USING (SELECT ? as city, ? as month, ? as day, ? as weather_main, ? as probability, ? as sample_count) AS source
                            ON target.city = source.city AND target.month = source.month AND target.day = source.day AND target.weather_main = source.weather_main
                            WHEN MATCHED THEN
                                UPDATE SET probability = source.probability, sample_count = source.sample_count, last_updated = GETDATE()
                            WHEN NOT MATCHED THEN
                                INSERT (city, month, day, weather_main, probability, sample_count)
                                VALUES (source.city, source.month, source.day, source.weather_main, source.probability, source.sample_count);
                        ''', (city, row['month'], row['day'], row['weather_main'], 
                             row['probability'], row['count']))
        
        conn.commit()
        conn.close()
    
    def get_daily_weather_probability(self, city: str, month: int, day: int) -> Dict:
        """Belirli bir gün için hava durumu olasılıklarını getir"""
        conn = self._get_connection()
        
        if "sqlite" in self.connection_string:
            query = '''
                SELECT weather_main, probability, sample_count
                FROM daily_probabilities 
                WHERE city = ? AND month = ? AND day = ?
                ORDER BY probability DESC
            '''
        else:
            query = '''
                SELECT weather_main, probability, sample_count
                FROM daily_probabilities 
                WHERE city = ? AND month = ? AND day = ?
                ORDER BY probability DESC
            '''
        
        df = pd.read_sql_query(query, conn, params=(city, month, day))
        conn.close()
        
        if df.empty:
            return {
                "city": city,
                "date": f"{month:02d}-{day:02d}",
                "weather_probabilities": {},
                "most_likely": "Unknown",
                "confidence": 0.0,
                "sample_count": 0
            }
        
        # Olasılıkları sözlüğe çevir
        probabilities = {}
        for _, row in df.iterrows():
            probabilities[row['weather_main']] = {
                "probability": row['probability'],
                "sample_count": row['sample_count']
            }
        
        # En olası hava durumunu bul
        most_likely = df.iloc[0]['weather_main']
        confidence = df.iloc[0]['probability']
        total_samples = df['sample_count'].sum()
        
        return {
            "city": city,
            "date": f"{month:02d}-{day:02d}",
            "weather_probabilities": probabilities,
            "most_likely": most_likely,
            "confidence": confidence,
            "sample_count": total_samples
        }
    
    def get_historical_examples(self, city: str, month: int, day: int, limit: int = 5) -> List[Dict]:
        """Belirli bir gün için geçmiş örnekleri getir"""
        conn = self._get_connection()
        
        if "sqlite" in self.connection_string:
            query = '''
                SELECT date, weather_main, weather_description, temperature, humidity, wind_speed
                FROM historical_weather 
                WHERE city = ? AND CAST(SUBSTR(date, 6, 2) AS INTEGER) = ? AND CAST(SUBSTR(date, 9, 2) AS INTEGER) = ?
                ORDER BY date DESC
                LIMIT ?
            '''
        else:
            query = '''
                SELECT TOP (?) date, weather_main, weather_description, temperature, humidity, wind_speed
                FROM historical_weather 
                WHERE city = ? AND CAST(SUBSTRING(date, 6, 2) AS INT) = ? AND CAST(SUBSTRING(date, 9, 2) AS INT) = ?
                ORDER BY date DESC
            '''
        
        if "sqlite" in self.connection_string:
            df = pd.read_sql_query(query, conn, params=(city, month, day, limit))
        else:
            df = pd.read_sql_query(query, conn, params=(limit, city, month, day))
        
        conn.close()
        
        examples = []
        for _, row in df.iterrows():
            examples.append({
                "year": row['date'][:4],
                "weather": row['weather_main'],
                "description": row['weather_description'],
                "temperature": row['temperature'],
                "humidity": row['humidity'],
                "wind_speed": row['wind_speed']
            })
        
        return examples
    
    def generate_training_data(self) -> pd.DataFrame:
        """ML modelleri için eğitim verisi oluştur"""
        conn = self._get_connection()
        
        if "sqlite" in self.connection_string:
            query = '''
                SELECT 
                    hw.city,
                    hw.date,
                    CAST(SUBSTR(hw.date, 6, 2) AS INTEGER) as month,
                    CAST(SUBSTR(hw.date, 9, 2) AS INTEGER) as day,
                    hw.weather_main,
                    hw.temperature,
                    hw.humidity,
                    hw.wind_speed,
                    dp.probability,
                    dp.sample_count
                FROM historical_weather hw
                LEFT JOIN daily_probabilities dp ON 
                    hw.city = dp.city AND 
                    CAST(SUBSTR(hw.date, 6, 2) AS INTEGER) = dp.month AND 
                    CAST(SUBSTR(hw.date, 9, 2) AS INTEGER) = dp.day AND
                    hw.weather_main = dp.weather_main
            '''
        else:
            query = '''
                SELECT 
                    hw.city,
                    hw.date,
                    CAST(SUBSTRING(hw.date, 6, 2) AS INT) as month,
                    CAST(SUBSTRING(hw.date, 9, 2) AS INT) as day,
                    hw.weather_main,
                    hw.temperature,
                    hw.humidity,
                    hw.wind_speed,
                    dp.probability,
                    dp.sample_count
                FROM historical_weather hw
                LEFT JOIN daily_probabilities dp ON 
                    hw.city = dp.city AND 
                    CAST(SUBSTRING(hw.date, 6, 2) AS INT) = dp.month AND 
                    CAST(SUBSTRING(hw.date, 9, 2) AS INT) = dp.day AND
                    hw.weather_main = dp.weather_main
            '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Şehir koordinatlarını ekle
        df['latitude'] = 0.0
        df['longitude'] = 0.0
        
        for city, coords in self.cities_data.items():
            mask = df['city'] == city
            df.loc[mask, 'latitude'] = coords['lat']
            df.loc[mask, 'longitude'] = coords['lon']
        
        return df
    
    def get_city_statistics(self, city: str) -> Dict:
        """Şehir için istatistiksel bilgiler"""
        conn = self._get_connection()
        
        # Toplam veri sayısı
        total_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM historical_weather WHERE city = ?", 
            conn, params=(city,)
        ).iloc[0]['count']
        
        # Hava durumu dağılımı
        weather_dist = pd.read_sql_query(
            "SELECT weather_main, COUNT(*) as count FROM historical_weather WHERE city = ? GROUP BY weather_main",
            conn, params=(city,)
        )
        
        # Sıcaklık istatistikleri
        temp_stats = pd.read_sql_query(
            "SELECT AVG(temperature) as avg_temp, MIN(temperature) as min_temp, MAX(temperature) as max_temp FROM historical_weather WHERE city = ?",
            conn, params=(city,)
        )
        
        conn.close()
        
        return {
            "city": city,
            "total_records": total_count,
            "weather_distribution": weather_dist.to_dict('records'),
            "temperature_stats": temp_stats.to_dict('records')[0]
        }

# Test fonksiyonu
if __name__ == "__main__":
    collector = HistoricalWeatherDataCollector()
    
    # Örnek kullanım
    print("📊 İstanbul 15 Aralık olasılıkları:")
    prob = collector.get_daily_weather_probability("İstanbul", 12, 15)
    print(json.dumps(prob, indent=2, ensure_ascii=False))
    
    print("\n📅 Geçmiş örnekler:")
    examples = collector.get_historical_examples("İstanbul", 12, 15)
    for example in examples:
        print(f"  {example['year']}: {example['weather']} ({example['temperature']}°C)") 