#!/usr/bin/env python3
"""
Basit ML servis testi
"""

import requests
import json

def test_ml_service():
    """ML servisini test et"""
    
    print("🧪 ML Servis Testi")
    print("=" * 50)
    
    # Test verisi
    test_data = {
        "cities": ["Kars"],
        "date": "2025-08-05",
        "user_weather_conditions": []
    }
    
    try:
        print("📡 ML servisine istek gönderiliyor...")
        print(f"🌐 URL: http://localhost:5001/predict_route")
        print(f"📦 Veri: {json.dumps(test_data, indent=2)}")
        print()
        
        # İstek gönder
        response = requests.post(
            "http://localhost:5001/predict_route",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"📊 Durum Kodu: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Başarılı!")
            print()
            
            # Sonuçları göster
            for prediction in result.get("predictions", []):
                city = prediction.get("city", "Bilinmiyor")
                weather = prediction.get("predicted_weather", "Bilinmiyor")
                confidence = prediction.get("confidence", 0.0)
                temperature = prediction.get("avg_temperature", 0.0)
                explanation = prediction.get("explanation", "Açıklama yok")
                sample_count = prediction.get("sample_count", 0)
                
                print(f"🏙️ Şehir: {city}")
                print(f"🌤️ Hava Durumu: {weather}")
                print(f"📊 Güven: {confidence:.2f}")
                print(f"🌡️ Sıcaklık: {temperature}°C")
                print(f"📈 Örnek Sayısı: {sample_count}")
                print(f"📝 Açıklama: {explanation}")
                print()
                
                if weather == "veri_yok":
                    print("🎯 SONUÇ: Sistem sadece gerçek tarihsel veri varsa tahmin yapıyor!")
                    print("✅ Bu, istediğiniz davranış!")
                elif sample_count > 0:
                    print("🎯 SONUÇ: Gerçek tarihsel veri kullanıldı!")
                    print(f"📊 Son {sample_count} yılın gerçek verisi analiz edildi.")
                else:
                    print("⚠️ SONUÇ: Beklenmeyen durum!")
                    
        else:
            print(f"❌ Hata: {response.status_code}")
            print(f"📄 Yanıt: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ML Servisine bağlanılamadı!")
        print("💡 ML servisinin çalıştığından emin olun:")
        print("   cd ml_service")
        print("   python advanced_weather_predictor.py")
    except requests.exceptions.Timeout:
        print("⏰ Zaman aşımı!")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

if __name__ == "__main__":
    test_ml_service() 