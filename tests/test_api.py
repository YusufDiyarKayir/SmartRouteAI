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
    lat = 41.0082 #enlem
    lon = 28.9784 #boylamı
    date = datetime(2024, 12, 15) #Test Tarihi
    timestamp = int(date.timestamp())
    
    url = f"http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={api_key}&units=metric&lang=tr"
    
    print("🔍 API Test Ediliyor...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10) #API'ye istek gönder
        print(f"Status Code: {response.status_code}") #API'nin döndüğü kod
        
        if response.status_code == 200:
            data = response.json() #API'nin döndüğü veriyi al
            print("✅ API çalışıyor!") #API'nin çalıştığını göster
            print(f"Veri: {data}") #API'nin döndüğü veriyi göster
        else:
            print(f"❌ API hatası: {response.text}") #API'nin döndüğü hata mesajını göster
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}") #Bağlantı hatasını göster

if __name__ == "__main__":
    test_api() 