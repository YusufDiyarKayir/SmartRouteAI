# 🚀 SmartRouteAI - Akıllı Rota Planlama Sistemi

Türkiye'ye özel, AI destekli gelişmiş rota planlama sistemi. Doğal dil işleme, ML tabanlı hava durumu tahmini, trafik analizi ve Google Maps entegrasyonu ile optimal rotalar hesaplar.

## 🌟 Mevcut Özellikler

### 🗺️ **Akıllı Rota Planlama**
- Doğal dil ile rota istekleri ("İstanbul'dan Ankara'ya git")
- Çoklu alternatif rota önerileri
- Google Maps Directions API entegrasyonu
- Koordinat tabanlı rota hesaplama

### 🌤️ **Tarihsel Veri Tabanlı Hava Durumu Sistemi**
- Son 5 yıllık gerçek hava durumu verileri
- SQL Server LocalDB ile güçlü veri saklama
- Gün bazında olasılık hesaplamaları
- Tarihsel patern analizi (%90+ güven)
- Gerçek zamanlı tahmin doğruluğu
- ML modelleri ile gelişmiş tahmin
- Frontend entegrasyonu ile canlı tahminler

### 🗓️ **Tatil ve Trafik Analizi**
- Abstract API ile tatil günü kontrolü
- Hafta sonu vs hafta içi trafik analizi
- Yoğun saat hesaplamaları (7-10, 17-20)
- Tatil dönemlerinde trafik yoğunluğu

### 💰 **Maliyet Hesaplama**
- Ücretli yollar ve köprüler tespiti
- Otoyol ücretleri analizi
- Toplam rota maliyeti hesaplama
- En ekonomik rota önerileri

### 💡 **Akıllı Öneriler**
- Hava koşullarına göre uyarılar
- Tatil dönemi önerileri
- Güvenlik ve süre optimizasyonu
- Öncelik seviyeli öneriler

## 🛠️ Sistem Gereksinimleri

- **Python 3.8+**
- **.NET 8.0**
- **Flask** (ML servisi için)
- **Google Maps API Key**
- **OpenWeatherMap API Key**
- **Abstract API Key** (tatil kontrolü için)

## 📦 Kurulum

### 1. Projeyi İndirin
```bash
git clone [repository-url]
cd LCW
```

### 2. Python Bağımlılıkları
```bash
cd ml_service
pip install flask flask-cors scikit-learn lightgbm joblib
```

### 3. .NET Bağımlılıkları
```bash
cd backend/SmartRouteAI.Backend
dotnet restore
```

### 4. API Anahtarları
Aşağıdaki API anahtarlarını `backend/SmartRouteAI.Backend/Program.cs` dosyasında güncelleyin:
- Google Maps API Key
- OpenWeatherMap API Key
- Abstract API Key

## 🧪 Test Sistemi

Projenin tüm bileşenlerini test etmek için kapsamlı bir test sistemi bulunmaktadır.

### Hızlı Test
```powershell
cd tests
.\run_tests.ps1
```

### Manuel Test
```bash
cd tests
python test_system.py
```

### Test Edilen Bileşenler
- ✅ Backend API sağlık kontrolü
- ✅ ML servisi sağlık kontrolü  
- ✅ Model dosyaları kontrolü
- ✅ AI model yükleme testi
- ✅ Prompt analizi testi
- ✅ Hava durumu tahmini testi
- ✅ Rota optimizasyonu testi
- ✅ Performans testi
- ✅ Hata yönetimi testi

Detaylı bilgi için [tests/README.md](tests/README.md) dosyasını inceleyin.

## 🚀 Hızlı Başlatma

### **Yöntem 1: Tarihsel Veri Tabanlı Sistem (Önerilen)**

#### Windows PowerShell:
```powershell
# Otomatik başlatma
.\start_historical_weather.ps1
```

### **Yöntem 2: Manuel Başlatma**

#### 1. SQL Server LocalDB Testi (İsteğe Bağlı)
```bash
python test_sql_server.py
```

#### 2. Tarihsel Verileri Topla (İsteğe Bağlı)
```bash
cd ml_service
python collect_historical_data.py --test
```

#### 3. Tarihsel Hava Durumu Servisi Başlat
```bash
cd ml_service
python historical_weather_predictor.py
```

#### 3. Backend Başlat (Yeni Terminal)
```bash
cd backend/SmartRouteAI.Backend
dotnet run
```

#### 4. Frontend Aç
Tarayıcıda http://localhost:5077 adresini açın

**Yeni Özellikler:**
- Tarihsel hava durumu tahminleri
- Gerçek zamanlı hava durumu analizi
- Geçmiş örnekler gösterimi
- Güven skorları

## 🌐 Erişim Adresleri

- **Frontend:** http://localhost:5077
- **Backend API:** http://localhost:5077
- **Tarihsel Hava Durumu:** http://localhost:5002
- **Swagger UI:** http://localhost:5077/swagger

## 📝 Kullanım Örnekleri

### Basit Rota
```
"İstanbul'dan Ankara'ya git"
```

### Tarihli Rota
```
"İstanbul'dan Kars'a 1 Temmuz git"
```

### Çoklu Durak
```
"Ankara'dan İzmir'e, oradan Antalya'ya en hızlı rota"
```

### Hava Koşullu Rota
```
"Yağmurlu havada İstanbul'dan Trabzon'a git"
```

## 🔧 API Endpoints

### Rota Planlama
```
POST /api/route/plan
Content-Type: application/json

{
  "prompt": "İstanbul'dan Ankara'ya git"
}
```

### Basit Rota Hesaplama
```
POST /route
Content-Type: application/json

{
  "fromLat": 41.0082,
  "fromLng": 28.9784,
  "toLat": 39.9334,
  "toLng": 32.8597,
  "date": "2024-12-25",
  "time": "10:00"
}
```

### ML Service Endpoints
```
GET  /health                    # Servis durumu
POST /predict_route            # Hava durumu tahmini
POST /route_recommendations    # Rota önerileri
POST /calculate_cost           # Maliyet hesaplama
```

## 📊 Sistem Mimarisi

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   ML Service    │
│   (Port 8080)   │◄──►│   (Port 5000)    │◄──►│   (Port 5000)   │
│                 │    │                  │    │                 │
│   - Leaflet     │    │   - Route        │    │   - Advanced    │
│   - HTML/CSS    │    │     Controller   │    │     Weather     │
│   - JavaScript  │    │   - Services     │    │     Predictor   │
│                 │    │   - Google Maps  │    │   - ML Models   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
    ┌────▼────┐            ┌─────▼─────┐            ┌────▼────┐
    │ User    │            │External   │            │Weather  │
    │ Input   │            │APIs       │            │Database │
    │         │            │           │            │         │
    └─────────┘            └───────────┘            └─────────┘
```

## 🎯 Özellik Detayları

### Doğal Dil İşleme
- **Prompt Analysis Service** ile Türkçe rota isteklerini analiz
- Şehir, tarih, saat ve özel istekleri çıkarma
- Köprü ve otoyol direktiflerini anlama

### ML Tabanlı Hava Durumu
- **81 il** için detaylı veri
- **Aylık** hava durumu paternleri
- **Olasılık** tabanlı tahminler
- **Güven skorları** ile doğruluk

### Trafik Analizi
- **Bayram dönemleri** trafik yoğunluğu
- **Hafta sonu** vs hafta içi analizi
- **Yoğun saat** hesaplamaları
- **Şehir tipine** göre trafik

### Maliyet Hesaplama
- **Otoyol ücretleri** (km başına)
- **Köprü geçiş** ücretleri
- **Toplam maliyet** hesaplama
- **En ekonomik** rota önerileri

## 🛑 Servisleri Durdurma

Tüm terminal pencerelerini kapatın veya:
- **Ctrl+C** ile her servisi durdurun
- **Terminal pencerelerini** kapatın

## 🔍 Sorun Giderme

### ML Servisi Çalışmıyor
```bash
cd ml_service
pip install -r requirements.txt
python advanced_weather_predictor.py
```

### Backend Çalışmıyor
```bash
cd backend/SmartRouteAI.Backend
dotnet restore
dotnet build
dotnet run
```

### Frontend Çalışmıyor
```bash
cd frontend
python -m http.server 8080
```

### Port Çakışması
- **Port 5000** kullanımdaysa backend portunu değiştirin
- **Port 8080** kullanımdaysa frontend portunu değiştirin

### API Anahtarı Hataları
- Google Maps API anahtarını kontrol edin
- OpenWeatherMap API anahtarını kontrol edin
- Abstract API anahtarını kontrol edin

## 📈 Gelecek Özellikler

- [ ] Gerçek zamanlı trafik verisi
- [ ] Yakıt tüketimi hesaplama
- [ ] CO2 emisyon analizi
- [ ] Mobil uygulama
- [ ] Çoklu dil desteği
- [ ] Kullanıcı hesap sistemi
- [ ] Rota geçmişi

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- **Proje Sahibi:** [Adınız]
- **Email:** [email@example.com]
- **GitHub:** [github-username]

---

**SmartRouteAI ile Türkiye'deki en akıllı rotaları planlayın! 🚗🗺️** 