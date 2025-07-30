#!/usr/bin/env python3
"""
SmartRouteAI - AI Service Starter
Bu script AI service'ini başlatır ve modelleri yükler.
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def check_dependencies():
    """Gerekli kütüphaneleri kontrol et"""
    print(" Bağımlılıklar kontrol ediliyor...")
    
    required_packages = [
        'tensorflow', 'flask', 'pandas', 'numpy', 
        'scikit-learn', 'joblib', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f" {package}")
        except ImportError:
            missing_packages.append(package)
            print(f" {package} - Eksik!")
    
    if missing_packages:
        print(f"\n Eksik paketler: {', '.join(missing_packages)}")
        print(" Kurulum için: pip install -r requirements.txt")
        return False
    
    print(" Tüm bağımlılıklar mevcut!")
    return True

def check_models():
    """AI modellerini kontrol et"""
    print("\n🤖 AI modelleri kontrol ediliyor...")
    
    # Model dosyalarının varlığını kontrol et
    required_files = [
        '../models/traffic_prediction_model.h5',
        '../models/traffic_prediction_scaler.pkl',
        '../models/traffic_prediction_metadata.json',
        '../models/route_optimization_model.h5',
        '../models/route_optimization_scaler.pkl',
        '../models/route_optimization_metadata.json'
    ]
    
    missing_models = []
    
    for model_file in required_files:
        if os.path.exists(model_file):
            print(f" {model_file}")
        else:
            missing_models.append(model_file)
            print(f" {model_file} - Eksik!")
    
    if missing_models:
        print(f"\n Eksik model dosyaları: {len(missing_models)}")
        print(" Model eğitimi için: python train_ai_models.py")
        return False
    
    print("Tüm AI modelleri mevcut!")
    return True

def start_ai_service():
    """AI service'ini başlat"""
    print("\n AI Service başlatılıyor...")
    
    # AI service dosyasının varlığını kontrol et
    if not os.path.exists('ai_service.py'):
        print("ai_service.py dosyası bulunamadı!")
        return False
    
    try:
        # AI service'i başlat
        process = subprocess.Popen([
            sys.executable, 'ai_service.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Service'in başlaması için bekle
        time.sleep(3)
        
        # Health check
        try:
            response = requests.get('http://localhost:5001/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"AI Service başarıyla başlatıldı!")
                print(f"Modeller yüklendi: {data.get('models_loaded', False)}")
                print(f"URL: http://localhost:5001")
                return process #Process objesini döndür
            else:
                print(f" Health check başarısız: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f" Health check hatası: {e}")
            return False
            
    except Exception as e:
        print(f"AI Service başlatma hatası: {e}")
        return False

def test_ai_endpoints():
    """AI endpoint'lerini test et"""
    print("\n AI endpoint'leri test ediliyor...")
    
    base_url = 'http://localhost:5001'
    
    # Test verisi
    test_data = {
        'route_info': {
            'distance': 100,
            'city_population': 1500000,
            'road_quality': 0.8,
            'highway_ratio': 0.4
        },
        'weather_data': {
            'condition': 'yağmurlu',
            'temperature': 15,
            'humidity': 70,
            'wind_speed': 20
        },
        'date_time': '2024-04-23T08:00:00'
    }
    
    try:
        # Trafik tahmini test
        response = requests.post(f'{base_url}/predict_traffic', json=test_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"Trafik tahmini: {result.get('traffic_multiplier', 0):.2f}x (Model: {result.get('model_used', 'Unknown')})")
        else:
            print(f"Trafik tahmini hatası: {response.status_code}")
            return False
        
        # Rota optimizasyonu test
        optimization_data = {
            **test_data,
            'traffic_data': {'multiplier': 1.2, 'level': 0.6},
            'user_preferences': {
                'duration_weight': 0.4,
                'cost_weight': 0.3,
                'comfort_weight': 0.3
            }
        }
        
        response = requests.post(f'{base_url}/optimize_route', json=optimization_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"Rota optimizasyonu: {result.get('optimized_duration', 0):.1f}dk (Skor: {result.get('optimization_score', 0):.2f})")
        else:
            print(f" Rota optimizasyonu hatası: {response.status_code}")
            return False
        
        # Model bilgileri test
        response = requests.get(f'{base_url}/model_info', timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f" Model bilgileri: Trafik={result.get('traffic_model', {}).get('type', 'Unknown')}, Rota={result.get('route_model', {}).get('type', 'Unknown')}")
        else:
            print(f" Model bilgileri hatası: {response.status_code}")
            return False
        
        print(" Tüm AI endpoint'leri çalışıyor!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Endpoint test hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print(" SmartRouteAI - AI Service Starter")
    print("=" * 50)
    
    # 1. Bağımlılıkları kontrol et
    if not check_dependencies():
        return False
    
    # 2. Modelleri kontrol et
    if not check_models():
        print("\nİpucu: Modelleri eğitmek için:")
        print("   python train_ai_models.py")
        return False
    
    # 3. AI service'i başlat
    process = start_ai_service()
    if not process:
        return False
    
    # 4. Endpoint'leri test et
    if not test_ai_endpoints():
        print(" AI endpoint testleri başarısız!")
        return False
    
    print("\nAI Service başarıyla başlatıldı ve test edildi!")
    print("Kullanılabilir endpoint'ler:")
    print("   - GET  /health - Servis durumu")
    print("   - POST /predict_traffic - Trafik tahmini")
    print("   - POST /optimize_route - Rota optimizasyonu")
    print("   - POST /generate_alternatives - Alternatif rotalar")
    print("   - GET  /model_info - Model bilgileri")
    print("\n Service çalışmaya devam ediyor... (Ctrl+C ile durdurun)")
    
    try:
        # Service'i çalışır durumda tut
        process.wait()
    except KeyboardInterrupt:
        print("\n⏹️ AI Service durduruluyor...")
        process.terminate()
        process.wait()
        print(" AI Service durduruldu.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 