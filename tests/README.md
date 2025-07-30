# 🧪 SmartRouteAI Test Sistemi

Bu klasör SmartRouteAI projesinin tüm test dosyalarını içerir.

## 📁 Dosya Yapısı

```
tests/
├── README.md              # Bu dosya
├── run_tests.ps1          # PowerShell test çalıştırıcı
├── test_system.py         # Ana kapsamlı test sistemi
├── test_api.py            # API testleri
├── test_localdb.py        # Veritabanı testleri
└── test_sql_connection.py # SQL bağlantı testleri
```

## 🚀 Test Sistemi Nasıl Çalıştırılır

### 1. PowerShell ile (Önerilen)
```powershell
cd tests
.\run_tests.ps1
```

### 2. Python ile
```bash
cd tests
python test_system.py
```

## 🧪 Test Edilen Bileşenler

### ✅ Sistem Sağlık Kontrolleri
- **Backend Sağlık Kontrolü**: ASP.NET Core API'nin çalışıp çalışmadığını kontrol eder
- **ML Servisi Sağlık Kontrolü**: Python Flask servisinin durumunu kontrol eder
- **Model Dosyaları Kontrolü**: Gerekli AI model dosyalarının varlığını kontrol eder

### 🤖 AI Model Testleri
- **AI Model Yükleme Testi**: Modellerin başarıyla yüklenip yüklenmediğini kontrol eder
- **Hava Durumu Tahmini Testi**: ML tabanlı hava durumu tahminlerini test eder

### 🔄 Fonksiyonel Testler
- **Prompt Analizi Testi**: Kullanıcı girdilerinin doğru analiz edilip edilmediğini kontrol eder
- **Rota Optimizasyonu Testi**: Rota hesaplama ve optimizasyon işlemlerini test eder
- **Performans Testi**: Sistem yanıt sürelerini ölçer
- **Hata Yönetimi Testi**: Hatalı girdilerin düzgün işlenip işlenmediğini kontrol eder

## 📊 Test Raporu

Test sistemi çalıştırıldıktan sonra ana dizinde `test_report.json` dosyası oluşturulur. Bu dosya şunları içerir:

- Test sonuçları ve başarı oranları
- Hata detayları
- Performans metrikleri
- Zaman damgaları

## 🔧 Gereksinimler

### Sistem Gereksinimleri
- Python 3.8+
- PowerShell 5.0+
- Backend çalışıyor olmalı (http://localhost:5077)
- ML servisi çalışıyor olmalı (http://localhost:5001)

### Python Paketleri
```bash
pip install requests
```

## 🚨 Sorun Giderme

### Backend Çalışmıyor
```bash
cd backend/SmartRouteAI.Backend
dotnet run
```

### ML Servisi Çalışmıyor
```bash
cd ml_service
python start_ai_service.py
```

### Model Dosyaları Eksik
```bash
cd ml_service
python train_ai_models.py
```

## 📈 Test Sonuçları

Test sistemi %80 başarı oranına ulaştığında başarılı kabul edilir. Başarısız testler için:

1. `test_report.json` dosyasını kontrol edin
2. Hata mesajlarını inceleyin
3. Gerekli servislerin çalıştığından emin olun
4. Model dosyalarının mevcut olduğunu kontrol edin

## 🔄 Sürekli Test

Geliştirme sırasında testleri sürekli çalıştırmak için:

```powershell
# Windows
while ($true) { .\run_tests.ps1; Start-Sleep 300 }

# Linux/Mac
while true; do python test_system.py; sleep 300; done
```

Bu komut testleri her 5 dakikada bir çalıştırır. 