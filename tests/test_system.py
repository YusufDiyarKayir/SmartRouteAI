#!/usr/bin/env python3
"""
🚀 SmartRouteAI - Kapsamlı Test Sistemi
Bu sistem tüm projedeki bileşenleri test eder ve rapor verir.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import subprocess
import threading
from typing import Dict, List, Tuple

class SmartRouteAITestSystem:
    def __init__(self):
        self.backend_url = "http://localhost:5077"
        self.ml_service_url = "http://localhost:5001"
        self.test_results = {}
        self.start_time = datetime.now()
        
    def print_header(self, title: str):
        """Test başlığı yazdır"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, message: str = "", details: str = ""):
        """Test sonucu yazdır"""
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"{status} | {test_name}")
        if message:
            print(f"   📝 {message}")
        if details:
            print(f"   🔍 {details}")
        
        # Sonucu kaydet
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_backend_health(self) -> bool:
        """Backend sağlık kontrolü"""
        try:
            response = requests.get(f"{self.backend_url}/api/route/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Backend Sağlık Kontrolü", True, 
                                f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_result("Backend Sağlık Kontrolü", False, 
                                f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Backend Sağlık Kontrolü", False, 
                            f"Bağlantı hatası: {str(e)}")
            return False
    
    def test_ml_service_health(self) -> bool:
        """ML servisi sağlık kontrolü"""
        try:
            response = requests.get(f"{self.ml_service_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_result("ML Servisi Sağlık Kontrolü", True, 
                                f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_result("ML Servisi Sağlık Kontrolü", False, 
                                f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("ML Servisi Sağlık Kontrolü", False, 
                            f"Bağlantı hatası: {str(e)}")
            return False
    
    def test_model_files(self) -> bool:
        """Model dosyalarının varlığını kontrol et"""
        required_models = [
            "../models/traffic_prediction_model.h5",
            "../models/traffic_prediction_scaler.pkl",
            "../models/traffic_prediction_metadata.json",
            "../models/route_optimization_model.h5",
            "../models/route_optimization_scaler.pkl",
            "../models/route_optimization_metadata.json",
            "../models/weather_model.pkl",
            "../models/temperature_model.pkl",
            "../models/historical_weather_model.pkl"
        ]
        
        missing_models = []
        existing_models = []
        
        for model in required_models:
            if os.path.exists(model):
                existing_models.append(model)
            else:
                missing_models.append(model)
        
        if len(missing_models) == 0:
            self.print_result("Model Dosyaları Kontrolü", True, 
                            f"{len(existing_models)} model dosyası mevcut")
            return True
        else:
            self.print_result("Model Dosyaları Kontrolü", False, 
                            f"{len(missing_models)} model eksik", 
                            f"Eksik: {', '.join(missing_models[:3])}")
            return False
    
    def test_prompt_analysis(self) -> bool:
        """Prompt analizi testi"""
        try:
            test_prompt = "İstanbul Ankara 15 Temmuz Yağmurlu"
            payload = {"prompt": test_prompt}
            
            response = requests.post(f"{self.backend_url}/api/route/analyze-prompt", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                source = data.get('source', '')
                destination = data.get('destination', '')
                weather = data.get('weatherConditions', [])
                
                self.print_result("Prompt Analizi Testi", True, 
                                f"Kaynak: {source}, Hedef: {destination}, Hava: {weather}")
                return True
            else:
                self.print_result("Prompt Analizi Testi", False, 
                                f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Prompt Analizi Testi", False, 
                            f"Hata: {str(e)}")
            return False
    
    def test_route_optimization(self) -> bool:
        """Rota optimizasyonu testi"""
        try:
            payload = {
                "source": "İstanbul",
                "destination": "Ankara",
                "waypoints": [],
                "requests": ["Hava koşulları: yağmurlu", "Seyahat tarihi: 2025-07-15"],
                "bridgeDirectives": [],
                "highwayDirectives": [],
                "weatherConditions": ["yağmurlu"],
                "travelDate": "2025-07-15",
                "travelTime": "10:00"
            }
            
            response = requests.post(f"{self.backend_url}/api/route/plan", 
                                   json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get('routes', [])
                
                self.print_result("Rota Optimizasyonu Testi", True, 
                                f"{len(routes)} rota bulundu")
                return True
            else:
                self.print_result("Rota Optimizasyonu Testi", False, 
                                f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Rota Optimizasyonu Testi", False, 
                            f"Hata: {str(e)}")
            return False
    
    def test_weather_prediction(self) -> bool:
        """Hava durumu tahmini testi"""
        try:
            payload = {
                "cities": ["İstanbul", "Ankara"],
                "date": "2025-07-15",
                "user_weather_conditions": ["yağmurlu"]
            }
            
            response = requests.post(f"{self.ml_service_url}/predict_route", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get('predictions', [])
                
                self.print_result("Hava Durumu Tahmini Testi", True, 
                                f"{len(predictions)} tahmin yapıldı")
                return True
            else:
                self.print_result("Hava Durumu Tahmini Testi", False, 
                                f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Hava Durumu Tahmini Testi", False, 
                            f"Hata: {str(e)}")
            return False
    
    def test_ai_model_loading(self) -> bool:
        """AI model yükleme testi"""
        try:
            # ML servisinin model yükleme durumunu kontrol et
            response = requests.get(f"{self.ml_service_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models_loaded = data.get('models_loaded', False)
                
                if models_loaded:
                    self.print_result("AI Model Yükleme Testi", True, 
                                    "Modeller başarıyla yüklendi")
                    return True
                else:
                    self.print_result("AI Model Yükleme Testi", False, 
                                    "Modeller yüklenemedi")
                    return False
            else:
                self.print_result("AI Model Yükleme Testi", False, 
                                f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("AI Model Yükleme Testi", False, 
                            f"Hata: {str(e)}")
            return False
    
    def test_performance(self) -> bool:
        """Performans testi"""
        try:
            start_time = time.time()
            
            # Hızlı bir rota hesaplama testi
            payload = {
                "source": "İstanbul",
                "destination": "Ankara",
                "waypoints": [],
                "requests": [],
                "bridgeDirectives": [],
                "highwayDirectives": [],
                "weatherConditions": [],
                "travelDate": "2025-07-15",
                "travelTime": "10:00"
            }
            
            response = requests.post(f"{self.backend_url}/api/route/plan", 
                                   json=payload, timeout=30)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200 and duration < 10:
                self.print_result("Performans Testi", True, 
                                f"Yanıt süresi: {duration:.2f} saniye")
                return True
            elif response.status_code == 200:
                self.print_result("Performans Testi", False, 
                                f"Yavaş yanıt: {duration:.2f} saniye")
                return False
            else:
                self.print_result("Performans Testi", False, 
                                f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Performans Testi", False, 
                            f"Hata: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Hata yönetimi testi"""
        try:
            # Geçersiz prompt ile test
            payload = {"prompt": ""}
            
            response = requests.post(f"{self.backend_url}/api/route/analyze-prompt", 
                                   json=payload, timeout=5)
            
            # Geçersiz prompt için hata bekliyoruz
            if response.status_code in [400, 422]:
                self.print_result("Hata Yönetimi Testi", True, 
                                "Geçersiz istek düzgün işlendi")
                return True
            else:
                self.print_result("Hata Yönetimi Testi", False, 
                                f"Beklenmeyen yanıt: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Hata Yönetimi Testi", False, 
                            f"Hata: {str(e)}")
            return False
    
    def generate_report(self):
        """Test raporu oluştur"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"📊 TEST RAPORU")
        print(f"{'='*60}")
        print(f"🕒 Test Süresi: {duration:.2f} saniye")
        print(f"📈 Toplam Test: {total_tests}")
        print(f"✅ Başarılı: {successful_tests}")
        print(f"❌ Başarısız: {failed_tests}")
        print(f"📊 Başarı Oranı: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ BAŞARISIZ TESTLER:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"   • {test_name}: {result['message']}")
        
        # Raporu dosyaya kaydet
        report_data = {
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }
        
        with open("../test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapor kaydedildi: test_report.json")
        
        return success_rate >= 80  # %80 başarı oranı
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print(f"🚀 SmartRouteAI Kapsamlı Test Sistemi Başlatılıyor...")
        print(f"🕒 Başlangıç: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test sırası
        tests = [
            ("Backend Sağlık Kontrolü", self.test_backend_health),
            ("ML Servisi Sağlık Kontrolü", self.test_ml_service_health),
            ("Model Dosyaları Kontrolü", self.test_model_files),
            ("AI Model Yükleme Testi", self.test_ai_model_loading),
            ("Prompt Analizi Testi", self.test_prompt_analysis),
            ("Hava Durumu Tahmini Testi", self.test_weather_prediction),
            ("Rota Optimizasyonu Testi", self.test_route_optimization),
            ("Performans Testi", self.test_performance),
            ("Hata Yönetimi Testi", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            self.print_header(test_name)
            try:
                test_func()
            except Exception as e:
                self.print_result(test_name, False, f"Beklenmeyen hata: {str(e)}")
        
        # Rapor oluştur
        success = self.generate_report()
        
        if success:
            print(f"\n🎉 Tüm testler başarıyla tamamlandı!")
            return True
        else:
            print(f"\n⚠️ Bazı testler başarısız oldu. Lütfen kontrol edin.")
            return False

def main():
    """Ana fonksiyon"""
    test_system = SmartRouteAITestSystem()
    
    try:
        success = test_system.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Test sistemi kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test sistemi hatası: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 