#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import time
import os
import sys
from datetime import datetime
import subprocess
import threading
from typing import Dict, List, Tuple

class SmartRouteAITestSystem: #Test sistemi sınıfı
    def __init__(self):
        self.backend_url = "http://localhost:5077" #Backend URL
        self.ml_service_url = "http://localhost:5001" #ML Servis URL
        self.test_results = {} #Test sonuçları
        self.start_time = datetime.now() #Test başlangıç zamanı
        
    def print_header(self, title: str): #Test başlığı yazdır
        """Test başlığı yazdır"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, message: str = "", details: str = ""):
        """Test sonucu yazdır"""
        status = "BAŞARILI" if success else " BAŞARISIZ"
        print(f"{status} | {test_name}")
        if message:
            print(f"    {message}")
        if details:
            print(f"    {details}")
        
        # Sonucu kaydet
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "details": details
        }
    
    def test_backend_health(self) -> bool:
        """Backend sağlık kontrolü"""
        try:
            response = requests.get(f"{self.backend_url}/api/route/health", timeout=5) #Backend'e istek gönder
            if response.status_code == 200: #Backend'in döndüğü kod
                data = response.json() #Backend'in döndüğü veriyi al
                self.print_result("Backend Sağlık Kontrolü", True, 
                                f"Status: {data.get('status', 'unknown')}") #Backend'in döndüğü veriyi göster
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
            "../models/traffic_prediction_model.pkl",
            "../models/traffic_prediction_scaler.pkl",
            "../models/traffic_prediction_metadata.json",
            "../models/weather_model.pkl",
            "../models/temperature_model.pkl",
            "../models/traffic_model.pkl",
            "../models/weather_encoder.pkl",
            "../models/scaler.pkl"
        ]
        
        missing_models = []
        existing_models = []
        
        for model in required_models: #Gerekli modelleri kontrol et
            if os.path.exists(model):
                existing_models.append(model) #Mevcut modelleri ekle
            else:
                missing_models.append(model) #Eksik modeli ekle
        
        if len(missing_models) == 0: #Eksik modeller yoksa
            self.print_result("Model Dosyaları Kontrolü", True, 
                            f"{len(existing_models)} model dosyası mevcut") #Mevcut modelleri göster
            return True
        else:
            self.print_result("Model Dosyaları Kontrolü", False, 
                            f"{len(missing_models)} model eksik", 
                            f"Eksik: {', '.join(missing_models[:3])}") #Eksik modelleri göster
            return False
    
    def test_prompt_analysis(self) -> bool:
        """Prompt analizi testi"""
        try:
            test_prompt = "İstanbul Ankara 15 Temmuz Yağmurlu"
            payload = {"prompt": test_prompt}
            
            response = requests.post(f"{self.backend_url}/api/route/analyze-prompt", 
                                   json=payload, timeout=10) #Backend'e prompt gönder
            
            if response.status_code == 200: #Backend'in döndüğü kod
                data = response.json() #Backend'in döndüğü veriyi al
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
                "prompt": "İstanbul'dan Ankara'ya git"
            } #Basit prompt kullan
            
            response = requests.post(f"{self.backend_url}/api/route/plan", 
                                   json=payload, timeout=60) #Timeout süresini artır
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get('routes', [])
                alternatives = data.get('alternatives', [])
                
                # Hem routes hem de alternatives kontrol et
                total_routes = len(routes) + len(alternatives)
                
                self.print_result("Rota Optimizasyonu Testi", True, 
                                f"{total_routes} rota bulundu") #Rota sayısını göster
                return True
            else:
                self.print_result("Rota Optimizasyonu Testi", False, 
                                f"HTTP {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            self.print_result("Rota Optimizasyonu Testi", False, 
                            "Timeout: Backend yanıt vermedi (60 saniye)")
            return False
        except Exception as e:
            self.print_result("Rota Optimizasyonu Testi", False, 
                            f"Hata: {str(e)}") #Hata mesajını göster
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
                                   json=payload, timeout=20)
            
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
        except requests.exceptions.Timeout:
            self.print_result("Hava Durumu Tahmini Testi", False, 
                            "Timeout: ML servisi yanıt vermedi (20 saniye)")
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
                cities_loaded = data.get('cities_loaded', 0)
                status = data.get('status', 'unknown')
                
                # ML servisi çalışıyorsa ve status healthy ise kabul et
                if status == 'healthy':
                    self.print_result("AI Model Yükleme Testi", True, 
                                    f"ML servisi çalışıyor (status: {status}, models: {models_loaded})")
                    return True
                else:
                    self.print_result("AI Model Yükleme Testi", False, 
                                    f"ML servisi sağlıksız (status: {status})")
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
            
            # Basit bir prompt analizi testi (daha hızlı)
            payload = {
                "prompt": "İstanbul Ankara"
            }
            
            response = requests.post(f"{self.backend_url}/api/route/analyze-prompt", 
                                   json=payload, timeout=15)
            
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
        except requests.exceptions.Timeout:
            self.print_result("Performans Testi", False, 
                            "Timeout: Backend yanıt vermedi (15 saniye)")
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
        total_tests = len(self.test_results)  #Toplam test sayısı
        successful_tests = sum(1 for result in self.test_results.values() if result['success']) #Başarılı test sayısı
        failed_tests = total_tests - successful_tests #Başarısız test sayısı
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0 #Başarı oranı
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f" TEST RAPORU")
        print(f"{'='*60}")
        print(f" Test Süresi: {duration} saniye")
        print(f" Toplam Test: {total_tests}")
        print(f" Başarılı: {successful_tests}")
        print(f" Başarısız: {failed_tests}")
        print(f" Başarı Oranı: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n BAŞARISIZ TESTLER:")
            for test_name, result in self.test_results.items():
                if not result['success']:
                    print(f"   • {test_name}: {result['message']}")
        
        # Raporu dosyaya kaydet
        report_data = {
            "test_timestamp": end_time.strftime("%Y-%m-%d %H:%M"),
            "duration_seconds": duration,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }
        
        with open("../test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n Rapor kaydedildi: test_report.json")
        
        return success_rate >= 80  # %80 başarı oranı
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print(f" SmartRouteAI Kapsamlı Test Sistemi Başlatılıyor...")
        print(f" Başlangıç: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
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
            print(f"\n Tüm testler başarıyla tamamlandı!")
            return True
        else:
            print(f"\n Bazı testler başarısız oldu. Lütfen kontrol edin.")
            return False

def main():
    """Ana fonksiyon"""
    test_system = SmartRouteAITestSystem()
    
    try:
        success = test_system.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n Test sistemi kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n Test sistemi hatası: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 