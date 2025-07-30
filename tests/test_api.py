#!/usr/bin/env python3
"""
OpenWeatherMap API Test Scripti
"""

import requests
from datetime import datetime

def test_api():
    """API'yi test et"""
    api_key = "0d97a7dabc935b1c450dbe82a3234617"
    
    # Test için İstanbul'un bugünkü verisi
    lat = 41.0082
    lon = 28.9784
    date = datetime(2024, 12, 15)
    timestamp = int(date.timestamp())
    
    url = f"http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={api_key}&units=metric&lang=tr"
    
    print("🔍 API Test Ediliyor...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API çalışıyor!")
            print(f"Veri: {data}")
        else:
            print(f"❌ API hatası: {response.text}")
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")

if __name__ == "__main__":
    test_api() 