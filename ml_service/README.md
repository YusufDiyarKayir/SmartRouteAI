# 🌤️ ML Weather Prediction Service

Bu servis, Türkiye şehirleri için tarih bazlı hava durumu tahmini yapan makine öğrenmesi servisidir.

## 🚀 Özellikler

- **Coğrafi Konum Bazlı Tahmin**: Türkiye'nin 81 ili için özelleştirilmiş hava durumu modelleri
- **Mevsimsel Analiz**: Kış, ilkbahar, yaz, sonbahar dönemlerine göre tahmin
- **Tarih Bazlı Tahmin**: Belirli tarihler için hava durumu öngörüsü
- **Güven Skoru**: Her tahmin için güvenilirlik oranı
- **Fallback Mekanizması**: ML servisi çalışmazsa varsayılan tahminler

## 📊 Desteklenen Hava Durumları

- **Kar/Karlı**: Doğu Anadolu bölgesi kış aylarında
- **Yağmur/Yağmurlu**: Karadeniz bölgesi ve yağışlı dönemler
- **Güneş/Güneşli**: Akdeniz, Ege ve yaz aylarında

## 🛠️ Kurulum

### 1. Python Ortamı Hazırlama

```bash
# Ana dizinde
cd ml_service

# Virtual environment oluştur
python -m venv venv

# Virtual environment aktifleştir
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
```

### 2. Gerekli Paketleri Yükle

```bash
pip install -r requirements.txt
```

### 3. Servisi Başlat

```bash
# Otomatik kurulum ve başlatma
python start_ml_service.py

# Veya manuel başlatma
python weather_predictor.py
```

## 🔗 API Endpoints

### Health Check
```
GET http://localhost:5000/health
```

### Tek Şehir Tahmini
```
POST http://localhost:5000/predict
Content-Type: application/json

{
    "city": "Kars",
    "date": "12 Aralık 2025"
}
```

### Rota Tahmini
```
POST http://localhost:5000/predict_route
Content-Type: application/json

{
    "cities": ["Diyarbakır", "Mardin", "Batman", "Tunceli", "Sinop", "Ordu"],
    "date": "15 Aralık 2025"
}
```

## 📈 Örnek Kullanım

### Backend Entegrasyonu

Backend'de ML servisi otomatik olarak çağrılır:

```csharp
// PromptAnalysisService'de otomatik entegrasyon
var weatherPredictions = await _weatherMLService.PredictWeatherForRouteAsync(cities, date);
```

### Test Örnekleri

```bash
# Kars için kış tahmini
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"city": "Kars", "date": "12 Aralık 2025"}'

# Rota tahmini
curl -X POST http://localhost:5000/predict_route \
  -H "Content-Type: application/json" \
  -d '{"cities": ["Diyarbakır", "Mardin", "Batman"], "date": "15 Aralık 2025"}'
```

## 🎯 Tahmin Mantığı

### Coğrafi Bölgeler

1. **Doğu Anadolu**: Kars, Erzurum, Ağrı, Van, Hakkari
   - Kış: Kar
   - Diğer mevsimler: Yağmur

2. **Karadeniz**: Trabzon, Rize, Ordu, Sinop, Artvin, Giresun
   - Tüm mevsimler: Yağmur

3. **Akdeniz**: Antalya, Mersin, Adana, Hatay, Muğla
   - Tüm mevsimler: Güneş

4. **Güneydoğu Anadolu**: Diyarbakır, Mardin, Batman, Şanlıurfa, Gaziantep
   - Kış: Yağmur
   - Diğer mevsimler: Güneş

5. **İç Anadolu**: Ankara, Konya, Kayseri
   - Kış: Kar
   - Diğer mevsimler: Yağmur/Güneş

## 🔧 Konfigürasyon

`appsettings.json` dosyasında ML servisi URL'si:

```json
{
  "MLService": {
    "Url": "http://localhost:5000"
  }
}
```

## 🚨 Sorun Giderme

### Servis Başlamıyor
```bash
# Port kontrolü
netstat -an | findstr :5000

# Python sürümü kontrolü
python --version

# Paket kontrolü
pip list
```

### Bağlantı Hatası
- ML servisinin çalıştığından emin olun
- Port 5000'in açık olduğunu kontrol edin
- Firewall ayarlarını kontrol edin

## 📝 Loglar

Servis çalışırken console'da şu logları göreceksiniz:

```
[ML SERVICE] Requesting weather prediction for 6 cities on 15 Aralık 2025
[ML SERVICE] Diyarbakır: güneş - Diyarbakır şehri winter mevsiminde tipik olarak güneş hava durumu yaşar.
[ML SERVICE] Mardin: güneş - Mardin şehri winter mevsiminde tipik olarak güneş hava durumu yaşar.
```

## 🔄 Güncelleme

Modeli güncellemek için:

```bash
# Model dosyasını sil (yeniden oluşturulacak)
rm weather_model.pkl

# Servisi yeniden başlat
python weather_predictor.py
``` 