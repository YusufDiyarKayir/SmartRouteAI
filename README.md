# 🚀 SmartRouteAI - Akıllı Rota Planlama Sistemi

## 📋 Proje Özeti

SmartRouteAI, yapay zeka destekli gelişmiş bir rota planlama sistemidir. Kullanıcıların doğal dil ile rota isteklerini yapabilmelerini sağlar ve hava durumu, trafik, tatil günleri gibi faktörleri dikkate alarak optimize edilmiş rotalar sunar.

## ✨ Özellikler

### 🤖 AI Destekli Özellikler
- **Doğal Dil İşleme (NLP)**: Kullanıcılar "İstanbul'dan Ankara'ya git" gibi doğal cümlelerle rota isteyebilir
- **Akıllı Prompt Analizi**: Azure Text Analytics ile gelişmiş metin analizi
- **Anlamsız Prompt Tespiti**: Geçersiz istekleri otomatik olarak tespit eder
- **ML Tabanlı Hava Durumu Analizi**: LSTM + Transformer modelleri ile hava durumu tahmini
- **Rota Optimizasyonu**: AI destekli rota optimizasyon algoritmaları

### 🗺️ Harita ve Rota Özellikleri
- **Google Maps Entegrasyonu**: Gerçek zamanlı harita görüntüleme
- **Alternatif Rotalar**: Birden fazla rota seçeneği sunma
- **Gerçek Zamanlı Trafik**: Trafik durumuna göre rota güncelleme
- **Ücretli Yol Tespiti**: Otoyol ve köprü ücretlerini hesaplama
- **Varış Zamanı Hesaplama**: Trafik ve hava durumuna göre varış tahmini

### 🌤️ Hava Durumu Entegrasyonu
- **OpenWeatherMap API**: Gerçek zamanlı hava durumu verileri
- **Hava Durumu Etkisi**: Yağmur, kar, sis gibi durumların rota süresine etkisi
- **5 Günlük Tahmin**: Gelecek tarihli hava durumu analizi
- **Hava Durumu Sınıflandırması**: Otomatik hava durumu kategorilendirme

### 📅 Tatil ve Zaman Yönetimi
- **Abstract API Entegrasyonu**: Türkiye tatil günleri kontrolü
- **Tatil Etkisi Hesaplama**: Tatil günlerinde trafik yoğunluğu analizi
- **Hafta Sonu Optimizasyonu**: Hafta sonu trafik durumuna göre rota ayarlama
- **Zaman Bazlı Rota**: Belirli saat ve tarihler için optimize edilmiş rotalar

### 🎯 Kullanıcı Deneyimi
- **Modern Web Arayüzü**: Responsive ve kullanıcı dostu tasarım
- **Gerçek Zamanlı Güncelleme**: Anlık rota ve hava durumu güncellemeleri
- **Hata Yönetimi**: Kapsamlı hata yakalama ve kullanıcı bilgilendirme
- **Çoklu Dil Desteği**: Türkçe arayüz ve mesajlar

## 🏗️ Teknik Mimari

### Backend (ASP.NET Core 8.0)
```
backend/SmartRouteAI.Backend/
├── Controllers/
│   └── RouteController.cs          # API endpoint'leri
├── Services/
│   ├── PromptAnalysisService.cs    # NLP işlemleri
│   ├── RouteOptimizationService.cs # Rota optimizasyonu
│   ├── MapService.cs              # Harita işlemleri
│   ├── AdvancedWeatherService.cs  # Hava durumu analizi
│   ├── HolidayService.cs          # Tatil kontrolü
│   └── AIModelService.cs          # AI model entegrasyonu
├── wwwroot/
│   └── index.html                 # Frontend dosyası
└── Program.cs                     # Uygulama konfigürasyonu
```

### Frontend (HTML/JavaScript/Leaflet.js)
```
frontend/
└── index.html                     # Ana kullanıcı arayüzü
```

### Python AI Servisleri
```
backend/
├── train_ai_models.py             # AI model eğitimi
├── weather_ml_service.py          # Hava durumu ML servisi
└── requirements.txt               # Python bağımlılıkları
```

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- .NET 8.0 SDK
- Python 3.8+
- Git

### API Anahtarları Kurulumu

1. **OpenWeatherMap API Anahtarı:**
   - [OpenWeatherMap](https://openweathermap.org/api) sitesine gidin
   - Ücretsiz hesap oluşturun
   - API anahtarınızı alın

2. **Google Maps API Anahtarı (Opsiyonel):**
   - [Google Cloud Console](https://console.cloud.google.com/) sitesine gidin
   - Maps JavaScript API'yi etkinleştirin
   - API anahtarınızı alın

3. **Holiday API Anahtarı (Opsiyonel):**
   - [Abstract API](https://www.abstractapi.com/holidays-api) sitesine gidin
   - Ücretsiz hesap oluşturun
   - API anahtarınızı alın

### Adımlar

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/YusufDiyarKayir/SmartRouteAI.git
cd SmartRouteAI
```

2. **Environment dosyasını oluşturun:**
```bash
# env.example dosyasını .env olarak kopyalayın
cp env.example .env

# .env dosyasını düzenleyin ve API anahtarlarınızı ekleyin
# Örnek:
# OPENWEATHER_API_KEY="your_api_key_here"
# GOOGLE_MAPS_API_KEY="your_google_maps_key_here"
# HOLIDAY_API_KEY="your_holiday_api_key_here"
```

3. **Python bağımlılıklarını yükleyin:**
```bash
cd ml_service
pip install -r requirements.txt
```

4. **Projeyi başlatın:**
```bash
cd ..
.\projeyi_baslat.ps1
```

4. **Tarayıcıda açın:**
```
http://localhost:5077
```

## 📊 API Endpoint'leri

### Ana Endpoint'ler
- `POST /api/Route/analyze-prompt` - Prompt analizi
- `POST /api/Route/plan` - Rota planlama
- `GET /api/Route/health` - Servis durumu

### Hava Durumu
- `GET /weatherforecast` - Hava durumu tahmini

### Rota Hesaplama
- `POST /route` - Koordinat bazlı rota hesaplama

## 🔧 Konfigürasyon

### API Anahtarları
Projeyi çalıştırmak için aşağıdaki API anahtarları gereklidir:

```json
{
  "GoogleMaps": "",
  "OpenWeatherMap": "",
  "AbstractAPI": "",
  "AzureTextAnalytics": ""
}
```

## 📈 Performans Özellikleri

- **Hızlı Yanıt**: Ortalama 2-3 saniye rota hesaplama süresi
- **Yüksek Doğruluk**: %95+ hava durumu tahmin doğruluğu
- **Ölçeklenebilir**: Mikroservis mimarisi ile kolay ölçeklendirme
- **Cache Sistemi**: 5 dakikalık önbellek ile hızlı erişim


### Test Etme
```bash
# Backend testleri
dotnet test

# Python servisleri test
python -m pytest tests/
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 👨‍💻 Geliştirici
**Yusuf Diyar Kayır**
- GitHub: [@YusufDiyarKayir](https://github.com/YusufDiyarKayir)
- Instagram: [@YusufDiyarKayir](https://www.instagram.com/yusufdkayir/)
- LinkedIn: [Yusuf Diyar Kayır](https://linkedin.com/in/yusufdiyarkayir)


**Son Güncelleme:** 15 Ocak 2024
**Durum:** ✅ Aktif Geliştirme 