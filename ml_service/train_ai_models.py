#!/usr/bin/env python3
"""
SmartRouteAI - AI Model Training Script
Bu script trafik tahmin ve rota optimizasyon modellerini eğitir.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import random
import os

# AI modellerini import et
from traffic_ai_model import TrafficPredictionAI
from route_optimization_ai import RouteOptimizationAI

def weather_code_to_str(code):
    mapping = {
        1: 'güneş',
        2: 'yağmur',
        3: 'kar',
        4: 'bulutlu',
        5: 'sis',
        6: 'fırtına',
        7: 'rüzgar'
    }
    return mapping.get(code, 'güneş')

def create_training_data():
    """Eğitim verisi oluştur"""
    print(" Eğitim verisi oluşturuluyor...")
    
    training_data = []
    
    # Eğitim süresini kısaltmak için veri miktarını azalt
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 6, 30)  # 6 ay yerine 6 ay
    current_date = start_date
    
    while current_date <= end_date:
        for hour in range(0, 24, 2):  # Her 2 saatte bir (12 veri noktası/gün)
            # Hava durumu simülasyonu
            weather_code = simulate_weather(current_date, current_date.month)
            temperature = simulate_temperature(current_date.month, hour)
            humidity = simulate_humidity(current_date.month, temperature)
            wind_speed = simulate_wind_speed(current_date.month)
            
            # Tatil kontrolü
            is_holiday = check_holiday(current_date)
            is_weekend = current_date.weekday() >= 5
            
            # Şehir bilgileri (Türkiye'nin 81 ili)
            cities = [
                {'name': 'Adana', 'population': 2200000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Adıyaman', 'population': 630000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Afyonkarahisar', 'population': 720000, 'road_quality': 0.75, 'highway_ratio': 0.4},
                {'name': 'Ağrı', 'population': 540000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Amasya', 'population': 330000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Ankara', 'population': 5500000, 'road_quality': 0.8, 'highway_ratio': 0.4},
                {'name': 'Antalya', 'population': 2500000, 'road_quality': 0.85, 'highway_ratio': 0.45},
                {'name': 'Artvin', 'population': 170000, 'road_quality': 0.6, 'highway_ratio': 0.2},
                {'name': 'Aydın', 'population': 1100000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Balıkesir', 'population': 1200000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Bilecik', 'population': 220000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Bingöl', 'population': 280000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Bitlis', 'population': 350000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Bolu', 'population': 310000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Burdur', 'population': 270000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Bursa', 'population': 3100000, 'road_quality': 0.8, 'highway_ratio': 0.4},
                {'name': 'Çanakkale', 'population': 540000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Çankırı', 'population': 190000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Çorum', 'population': 530000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Denizli', 'population': 1000000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Diyarbakır', 'population': 1700000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Edirne', 'population': 410000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Elazığ', 'population': 580000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Erzincan', 'population': 230000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Erzurum', 'population': 760000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Eskişehir', 'population': 870000, 'road_quality': 0.8, 'highway_ratio': 0.4},
                {'name': 'Gaziantep', 'population': 2100000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Giresun', 'population': 450000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Gümüşhane', 'population': 150000, 'road_quality': 0.6, 'highway_ratio': 0.2},
                {'name': 'Hakkari', 'population': 280000, 'road_quality': 0.55, 'highway_ratio': 0.15},
                {'name': 'Hatay', 'population': 1600000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Isparta', 'population': 440000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Mersin', 'population': 1800000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'İstanbul', 'population': 16000000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'İzmir', 'population': 4300000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Kars', 'population': 290000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Kastamonu', 'population': 380000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Kayseri', 'population': 1400000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Kırklareli', 'population': 360000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Kırşehir', 'population': 240000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Kocaeli', 'population': 2000000, 'road_quality': 0.8, 'highway_ratio': 0.4},
                {'name': 'Konya', 'population': 2200000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Kütahya', 'population': 580000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Malatya', 'population': 800000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Manisa', 'population': 1400000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Kahramanmaraş', 'population': 1100000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Mardin', 'population': 840000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Muğla', 'population': 980000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Muş', 'population': 410000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Nevşehir', 'population': 300000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Niğde', 'population': 360000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Ordu', 'population': 760000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Rize', 'population': 340000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Sakarya', 'population': 1000000, 'road_quality': 0.8, 'highway_ratio': 0.4},
                {'name': 'Samsun', 'population': 1300000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Siirt', 'population': 330000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Sinop', 'population': 220000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Sivas', 'population': 640000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Tekirdağ', 'population': 1100000, 'road_quality': 0.8, 'highway_ratio': 0.4},
                {'name': 'Tokat', 'population': 600000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Trabzon', 'population': 810000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Tunceli', 'population': 84000, 'road_quality': 0.6, 'highway_ratio': 0.2},
                {'name': 'Şanlıurfa', 'population': 2100000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Uşak', 'population': 370000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Van', 'population': 1100000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Yozgat', 'population': 420000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Zonguldak', 'population': 600000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Aksaray', 'population': 420000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Bayburt', 'population': 82000, 'road_quality': 0.6, 'highway_ratio': 0.2},
                {'name': 'Karaman', 'population': 250000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Kırıkkale', 'population': 280000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Batman', 'population': 620000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Şırnak', 'population': 530000, 'road_quality': 0.6, 'highway_ratio': 0.2},
                {'name': 'Bartın', 'population': 200000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Ardahan', 'population': 99000, 'road_quality': 0.6, 'highway_ratio': 0.2},
                {'name': 'Iğdır', 'population': 200000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Yalova', 'population': 270000, 'road_quality': 0.75, 'highway_ratio': 0.35},
                {'name': 'Karabük', 'population': 250000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Kilis', 'population': 140000, 'road_quality': 0.65, 'highway_ratio': 0.25},
                {'name': 'Osmaniye', 'population': 530000, 'road_quality': 0.7, 'highway_ratio': 0.3},
                {'name': 'Düzce', 'population': 390000, 'road_quality': 0.75, 'highway_ratio': 0.35}
            ]
            
            for city in cities:
                # Rota mesafesi (50-300 km arası)
                route_distance = random.randint(50, 300)
                
                # Trafik çarpanı hesaplama
                traffic_multiplier = calculate_realistic_traffic_multiplier(
                    hour, current_date.weekday(), current_date.month, 
                    is_holiday, is_weekend, weather_code, temperature, city['population']
                )
                
                # Gerçek süre hesaplama (trafik ve hava durumu etkisi ile)
                base_duration = route_distance * 1.2  # km başına 1.2 dakika
                weather_impact = calculate_weather_impact(weather_code)
                actual_duration = base_duration * traffic_multiplier * weather_impact
                
                # Maliyet hesaplama
                base_cost = route_distance * 0.8  # km başına 0.8 TL
                actual_cost = base_cost * weather_impact
                
                # Konfor skoru
                comfort_score = calculate_comfort_score(city['road_quality'], weather_code, traffic_multiplier)
                
                # Veri noktası oluştur
                data_point = {
                    'timestamp': current_date.replace(hour=hour).isoformat(),
                    'weather_condition': weather_code_to_str(weather_code),
                    'traffic_level': traffic_multiplier,
                    'distance': route_distance,
                    'duration': actual_duration,
                    'cost': actual_cost,
                    'comfort_score': comfort_score,
                    'city_population': city['population'],
                    'road_quality': city['road_quality'],
                    'highway_ratio': city['highway_ratio'],
                    'temperature': temperature,
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                    'is_holiday': is_holiday,
                    'is_weekend': is_weekend,
                    'hour': hour,
                    'day_of_week': current_date.weekday(),
                    'month': current_date.month
                }
                
                training_data.append(data_point)
        
        current_date += timedelta(days=1)
    
    print(f" {len(training_data)} veri noktası oluşturuldu")
    return training_data

def check_holiday(date):
    """Tatil kontrolü"""
    holidays_2023 = [
        '2023-01-01', '2023-04-21', '2023-04-22', '2023-04-23',
        '2023-05-01', '2023-05-19', '2023-06-28', '2023-06-29',
        '2023-06-30', '2023-07-01', '2023-07-15', '2023-08-30',
        '2023-10-29'
    ]
    holidays_2024 = [
        '2024-01-01', '2024-04-10', '2024-04-11', '2024-04-12',
        '2024-04-23', '2024-05-01', '2024-05-19', '2024-06-17',
        '2024-06-18', '2024-06-19', '2024-06-20', '2024-07-15',
        '2024-08-30', '2024-10-29'
    ]
    
    date_str = date.strftime('%Y-%m-%d')
    return date_str in holidays_2023 or date_str in holidays_2024

def simulate_weather(date, month):
    """Hava durumu simülasyonu"""
    # Mevsimsel hava durumu
    if month in [12, 1, 2]:  # Kış
        return np.random.choice([2, 4, 5], p=[0.3, 0.5, 0.2])  # Kar, bulutlu, sis
    elif month in [3, 4, 5]:  # İlkbahar
        return np.random.choice([1, 3, 4], p=[0.4, 0.4, 0.2])  # Yağmur, güneş, bulutlu
    elif month in [6, 7, 8]:  # Yaz
        return np.random.choice([3, 4, 6], p=[0.6, 0.3, 0.1])  # Güneş, bulutlu, fırtına
    else:  # Sonbahar
        return np.random.choice([1, 3, 4], p=[0.3, 0.4, 0.3])  # Yağmur, güneş, bulutlu

def simulate_temperature(month, hour):
    """Sıcaklık simülasyonu"""
    # Mevsimsel sıcaklık
    base_temp = {
        1: 5, 2: 7, 3: 12, 4: 17, 5: 22, 6: 27,
        7: 30, 8: 29, 9: 24, 10: 18, 11: 12, 12: 7
    }
    
    base = base_temp[month]
    hour_variation = np.sin((hour - 6) * np.pi / 12) * 5  # Günlük değişim
    random_variation = np.random.normal(0, 3)  # Rastgele değişim
    
    return base + hour_variation + random_variation

def simulate_humidity(month, temperature):
    """Nem simülasyonu"""
    # Sıcaklık ve mevsime bağlı nem
    if temperature < 10:
        return np.random.uniform(60, 90)
    elif temperature > 25:
        return np.random.uniform(30, 60)
    else:
        return np.random.uniform(40, 80)

def simulate_wind_speed(month):
    """Rüzgar hızı simülasyonu"""
    # Mevsimsel rüzgar
    if month in [3, 4, 10, 11]:  # İlkbahar ve sonbahar
        return np.random.uniform(15, 35)
    else:
        return np.random.uniform(5, 20)

def calculate_realistic_traffic_multiplier(hour, day_of_week, month, is_holiday, is_weekend, weather_code, temperature, city_population):
    """Gerçekçi trafik çarpanı hesaplama"""
    base_multiplier = 1.0
    
    # Rush hour etkisi
    if 7 <= hour <= 9:  # Sabah rush
        base_multiplier *= 1.4
    elif 17 <= hour <= 19:  # Akşam rush
        base_multiplier *= 1.5
    elif 12 <= hour <= 14:  # Öğle
        base_multiplier *= 1.2
    
    # Hafta sonu etkisi
    if is_weekend:
        base_multiplier *= 1.3
    
    # Tatil etkisi
    if is_holiday:
        base_multiplier *= 1.2
    
    # Hava durumu etkisi
    if weather_code == 1:  # Yağmur
        base_multiplier *= 1.15
    elif weather_code == 2:  # Kar
        base_multiplier *= 1.3
    elif weather_code == 6:  # Fırtına
        base_multiplier *= 1.25
    
    # Şehir büyüklüğü etkisi
    if city_population > 1000000:
        base_multiplier *= 1.1
    
    # Mevsimsel etki
    if month in [7, 8]:  # Yaz tatili
        base_multiplier *= 1.1
    
    return min(max(base_multiplier, 0.5), 3.0)

def calculate_weather_impact(weather_code):
    """Hava durumu etkisi"""
    impacts = {
        1: 1.1,  # Yağmur - %10 artış
        2: 1.15, # Kar - %15 artış
        3: 1.0,  # Güneş - Etki yok
        4: 1.02, # Bulutlu - %2 artış
        5: 1.08, # Sis - %8 artış
        6: 1.12, # Fırtına - %12 artış
        7: 1.03  # Rüzgar - %3 artış
    }
    return impacts.get(weather_code, 1.0)

def calculate_comfort_score(road_quality, weather_code, traffic_multiplier):
    """Konfor skoru hesaplama"""
    base_comfort = 0.7
    
    # Yol kalitesi etkisi
    comfort = base_comfort * road_quality
    
    # Hava durumu etkisi
    if weather_code in [1, 2, 5, 6]:  # Kötü hava
        comfort *= 0.8
    elif weather_code == 3:  # Güneş
        comfort *= 1.1
    
    # Trafik yoğunluğu etkisi
    comfort *= (1 - (traffic_multiplier - 1) * 0.2)
    
    return min(max(comfort, 0.1), 1.0)

def calculate_safety_score(road_quality, weather_code, highway_ratio):
    """Güvenlik skoru hesaplama"""
    base_safety = 0.8
    
    # Yol kalitesi etkisi
    safety = base_safety * road_quality
    
    # Hava durumu etkisi
    if weather_code == 2:  # Kar
        safety *= 0.6
    elif weather_code in [1, 5]:  # Yağmur, sis
        safety *= 0.8
    elif weather_code == 6:  # Fırtına
        safety *= 0.7
    
    # Otoyol etkisi
    safety *= (0.9 + highway_ratio * 0.1)
    
    return min(max(safety, 0.1), 1.0)

def train_models():
    """AI modellerini eğit"""
    print(" AI modelleri eğitiliyor...")
    
    # Eğitim verisi oluştur
    training_data = create_training_data()
    
    # Models klasörünü oluştur
    os.makedirs('../models', exist_ok=True)
    
    # 1. Trafik tahmin modeli eğitimi
    print("\n Trafik tahmin modeli eğitiliyor...")
    traffic_ai = TrafficPredictionAI()
    traffic_ai.train(training_data)
    traffic_ai.save_model('../models/traffic_prediction')
    
    print(" Trafik modeli eğitildi")
    
    # 2. Rota optimizasyon modeli eğitimi
    print("\n Rota optimizasyon modeli eğitiliyor...")
    route_ai = RouteOptimizationAI()
    route_ai.train(training_data)
    route_ai.save_model('../models/route_optimization')
    
    print(" Rota modeli eğitildi")
    
    # Eğitim sonuçlarını kaydet
    training_results = {
        'training_date': datetime.now().isoformat(),
        'data_points': len(training_data),
        'traffic_model': {
            'model_type': 'RandomForest',
            'status': 'trained'
        },
        'route_model': {
            'model_type': 'RandomForest',
            'status': 'trained'
        }
    }
    
    with open('../models/training_results.json', 'w') as f:
        json.dump(training_results, f, indent=2)
    
    print("\n Model eğitimi tamamlandı!")
    print(f" Eğitim sonuçları: ../models/training_results.json")
    
    return training_results

def test_models():
    """Eğitilen modelleri test et"""
    print("\n Modeller test ediliyor...")
    
    # Modelleri yükle
    traffic_ai = TrafficPredictionAI()
    route_ai = RouteOptimizationAI()
    
    try:
        traffic_ai.load_model('../models/traffic_prediction')
        route_ai.load_model('../models/route_optimization')
        
        # Test verisi
        test_route_info = {
            'distance': 100,
            'city_population': 1500000,
            'road_quality': 0.8,
            'highway_ratio': 0.4
        }
        
        test_weather_data = {
            'condition': 'yağmurlu',
            'temperature': 15,
            'humidity': 70,
            'wind_speed': 20
        }
        
        test_date = datetime(2024, 4, 23, 8, 0)  # Tatil günü, rush hour
        
        # Trafik tahmini test
        traffic_prediction = traffic_ai.predict_traffic(test_route_info, test_weather_data, test_date)
        print(f" Trafik tahmini: {traffic_prediction:.2f}x")
        
        # Rota optimizasyonu test
        test_traffic_data = {'traffic_multiplier': traffic_prediction}
        test_user_prefs = {'duration_weight': 0.4, 'cost_weight': 0.3, 'comfort_weight': 0.3}
        
        optimization = route_ai.optimize_route(
            test_route_info, test_weather_data, test_traffic_data, test_user_prefs
        )
        
        print(f" Rota optimizasyonu:")
        print(f"   - Süre: {optimization['duration']:.1f} dakika")
        print(f"   - Maliyet: {optimization['cost']:.0f} TL")
        print(f"   - Konfor: {optimization['comfort_score']:.2f}")
        print(f"   - Skor: {optimization['optimization_score']:.2f}")
        
        print(" Model testleri başarılı!")
        
    except Exception as e:
        print(f" Model test hatası: {e}")

if __name__ == "__main__":
    print(" SmartRouteAI - AI Model Training")
    print("=" * 50)
    
    try:
        # Modelleri eğit
        results = train_models()
        
        # Test et
        test_models()
        
        print("\n Eğitim tamamlandı! Modeller kullanıma hazır.")
        
    except Exception as e:
        print(f" Eğitim hatası: {e}")
        sys.exit(1) 