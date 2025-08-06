#!/usr/bin/env python3


import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    print("OPENWEATHER_API_KEY .env dosyasında bulunamadı!")
    print(" Lütfen .env dosyasını oluşturun ve API anahtarınızı ekleyin.")
    exit(1)

def test_current_weather(city):
    """Güncel hava durumu testi"""
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': f"{city},TR",
        'appid': API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f" {city}: {data['weather'][0]['main']} ({data['main']['temp']}°C)")
            return data
        else:
            print(f" {city}: API Error {response.status_code}")
            return None
    except Exception as e:
        print(f" {city}: {e}")
        return None

def test_historical_data(city, date_str):
    """Tarihsel veri testi"""
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': f"{city},TR",
        'appid': API_KEY,
        'units': 'metric',
        'dt': int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f" {city} ({date_str}): {data['weather'][0]['main']} ({data['main']['temp']}°C)")
            return data
        else:
            print(f" {city} ({date_str}): API Error {response.status_code}")
            return None
    except Exception as e:
        print(f" {city} ({date_str}): {e}")
        return None

if __name__ == "__main__":
    print(" OpenWeatherMap API Test")
    print("=" * 50)
    
    # Test şehirleri
    test_cities = ["Istanbul", "Kars", "Iğdır", "Antalya", "Trabzon"]
    
    print("\n Güncel Hava Durumu Testi:")
    for city in test_cities:
        test_current_weather(city)
    
    print("\n Tarihsel Veri Testi:")
    test_dates = ["2023-12-12", "2022-12-12", "2021-12-12"]
    
    for city in ["Kars", "Iğdır"]:
        for date in test_dates:
            test_historical_data(city, date)
            import time
            time.sleep(1)  # API limit aşımını önle
    
    print("\n API Test tamamlandı!") 