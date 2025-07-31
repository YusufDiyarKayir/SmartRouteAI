from advanced_weather_data import MLWeatherDatabase
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random

class AdvancedWeatherPredictor:
    def __init__(self):
        self.db = MLWeatherDatabase() #MLWeatherDatabase sınıfından bir örnek oluştur
        print("🌤️ ML Tabanlı Hava Durumu Tahmin Sistemi Başlatıldı")
        print(f"📊 {len(self.db.cities_data)} şehir için ML modelleri hazır")
    
    #Rota üzerindeki tüm şehirler için gelişmiş hava durumu tahmini
    def predict_route_weather(self, cities: List[str], date_str: str, user_weather_conditions: List[str] = None) -> Dict:
        """Rota üzerindeki şehirler için hava durumu tahmini"""
        try:
            print(f"[ML] Rota hava durumu tahmini: {cities} - {date_str}")
            if user_weather_conditions:
                print(f"[ML] Kullanıcı hava durumu koşulları: {user_weather_conditions}")
            
            # Tarih bilgilerini çıkar
            month = self._extract_month_from_date(date_str)
            year = self._extract_year_from_date(date_str)
            season = self._get_season(month)
            
            predictions = []
            
            for city in cities:
                try:
                    # Kullanıcının istediği hava durumu varsa onu kullan
                    if user_weather_conditions and len(user_weather_conditions) > 0:
                        predicted_weather = user_weather_conditions[0]  # İlk koşulu kullan
                        confidence = 0.95  # Kullanıcı belirttiği için yüksek güven
                        print(f"[ML] Kullanıcı hava durumu kullanılıyor: {city} -> {predicted_weather}")
                        # Kullanıcı isteğine göre sıcaklık ata
                        if 'kar' in predicted_weather:
                            avg_temperature = 0
                        elif 'yağmur' in predicted_weather:
                            avg_temperature = 8
                        elif 'bulut' in predicted_weather:
                            avg_temperature = 12
                        elif 'sis' in predicted_weather:
                            avg_temperature = 5
                        elif 'fırtına' in predicted_weather:
                            avg_temperature = 10
                        elif 'rüzgar' in predicted_weather:
                            avg_temperature = 10
                        else:
                            avg_temperature = 20
                        explanation = f"Kullanıcı isteği: {city} için {predicted_weather} hava durumu"
                    else:
                        # ML tahmini yap
                        weather_pred = self.db.predict_weather_for_city_date(city, date_str)
                        predicted_weather = weather_pred["predicted_weather"]
                        confidence = weather_pred["confidence"]
                        avg_temperature = self.db.get_average_temperature(city, month)
                        explanation = f"{city} için {predicted_weather} hava durumu bekleniyor"
                        print(f"[ML] ML tahmini kullanılıyor: {city} -> {predicted_weather}")
                    
                    # Hava durumuna göre süre etkisi
                    weather_duration_impact = self._calculate_weather_duration_impact(predicted_weather)
                    print(f"[ML] Hava durumu etkisi: {predicted_weather} -> {weather_duration_impact}x")
                    
                    # Tatil kontrolü
                    is_holiday, holiday_name = self._check_holiday_simple(date_str)
                    
                    # Trafik çarpanı hesaplama
                    traffic_multiplier = self.db.calculate_traffic_multiplier(city, month, is_holiday)
                    
                    # Trafik açıklaması
                    traffic_explanation = self._get_traffic_explanation(city, traffic_multiplier, is_holiday, holiday_name)
                    
                    prediction = {
                        "city": city,
                        "date": date_str,
                        "month": month,
                        "season": season,
                        "predicted_weather": predicted_weather,
                        "confidence": confidence,
                        "avg_temperature": avg_temperature,
                        "climate_zone": self.db.get_climate_zone(city),
                        "traffic_multiplier": traffic_multiplier,
                        "weather_duration_impact": weather_duration_impact,
                        "is_holiday": is_holiday,
                        "holiday_name": holiday_name,
                        "explanation": explanation,
                        "traffic_explanation": traffic_explanation
                    }
                    
                    predictions.append(prediction)
                    print(f"[ML] Tahmin tamamlandı: {city} -> {predicted_weather} (güven: {confidence})")
                    
                except Exception as e:
                    print(f"[ML] {city} için tahmin hatası: {e}")
                    # Fallback tahmin
                    predictions.append({
                        "city": city,
                        "date": date_str,
                        "month": month,
                        "season": season,
                        "predicted_weather": "güneş",
                        "confidence": 0.6,
                        "avg_temperature": 15,
                        "climate_zone": "Bilinmiyor",
                        "traffic_multiplier": 1.0,
                        "weather_duration_impact": 1.0,
                        "is_holiday": False,
                        "holiday_name": "",
                        "explanation": f"{city} için varsayılan tahmin",
                        "traffic_explanation": f"{city} şehrinde normal trafik yoğunluğu"
                    })
            
            # Rota özeti
            route_summary = {
                "total_cities": len(cities),
                "avg_confidence": sum([p["confidence"] for p in predictions]) / len(predictions) if predictions else 0.6,
                "is_holiday_period": any([p["is_holiday"] for p in predictions]),
                "holiday_name": next((p["holiday_name"] for p in predictions if p["is_holiday"]), ""),
                "weather_conditions": list(set([p["predicted_weather"] for p in predictions])),
                "climate_zones": list(set([p["climate_zone"] for p in predictions])),
                "avg_traffic_multiplier": sum([p["traffic_multiplier"] for p in predictions]) / len(predictions) if predictions else 1.0,
                "total_duration_impact": sum([p["weather_duration_impact"] for p in predictions]) / len(predictions) if predictions else 1.0
            }
            
            return {
                "predictions": predictions,
                "route_summary": route_summary
            }
            
        except Exception as e:
            print(f"[ML] Rota tahmin hatası: {e}")
            return self._get_fallback_predictions(cities, date_str)
    
    def _extract_month_from_date(self, date_str: str) -> int:
        """Tarih string'inden ay numarasını çıkar"""
        try:
            month_names = {
                "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6,
                "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12
            }
            
            # Tarih formatını kontrol et
            import re
            iso_pattern = r'(\d{4})-(\d{1,2})-\d{1,2}'
            iso_match = re.search(iso_pattern, date_str)
            if iso_match:
                month = int(iso_match.group(2))
                print(f"[DEBUG] ISO format detected: {date_str} -> Month: {month}")
                return month
            
            # Tarih formatını kontrol et
            day_month_pattern = r'(\d{1,2})\s*(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)'
            match = re.search(day_month_pattern, date_str.lower())
            if match:
                month_name = match.group(2)
                month = month_names[month_name]
                print(f"[DEBUG] Day-Month format detected: {date_str} -> Month: {month}")
                return month
            
            # Ay adını ara
            parts = date_str.lower().split()
            for part in parts:
                if part in month_names:
                    month = month_names[part]
                    print(f"[DEBUG] Month name detected: {date_str} -> Month: {month}")
                    return month
            
            # Varsayılan olarak şu anki ay
            print(f"[DEBUG] Default month used: {date_str} -> Month: {datetime.now().month}")
            return datetime.now().month
        except Exception as e:
            print(f"[DEBUG] Error in _extract_month_from_date: {e}")
            return datetime.now().month
    
    def _extract_year_from_date(self, date_str: str) -> int:
        """Tarih string'inden yıl numarasını çıkar"""
        try:
            parts = date_str.split()
            for part in parts:
                if part.isdigit() and len(part) == 4:
                    return int(part)
            return datetime.now().year
        except:
            return datetime.now().year
    
    def _get_season(self, month: int) -> str:
        """Ay numarasına göre mevsim döndür"""
        if month in [12, 1, 2]:
            return "kış"
        elif month in [3, 4, 5]:
            return "ilkbahar"
        elif month in [6, 7, 8]:
            return "yaz"
        else:
            return "sonbahar"
    
    def _calculate_weather_duration_impact(self, weather: str) -> float:
        """Hava durumuna göre süre etkisi çarpanı"""
        impacts = {
            "kar": 1.15,     # %15 artış
            "karlı": 1.15,   # %15 artış
            "yağmur": 1.1,   # %10 artış
            "yağmurlu": 1.1, # %10 artış
            "sis": 1.08,     # %8 artış
            "sisli": 1.08,   # %8 artış
            "güneş": 1.0,    # Etki yok
            "güneşli": 1.0   # Etki yok
        }
        return impacts.get(weather, 1.0)
    
    def _check_holiday_simple(self, date_str: str) -> Tuple[bool, str]:
        """Basit tatil kontrolü (HolidayService backend'de yapılıyor)"""
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Sabit tatiller
            fixed_holidays = {
                (1, 1): "Yılbaşı",
                (4, 23): "Ulusal Egemenlik ve Çocuk Bayramı",
                (5, 1): "Emek ve Dayanışma Günü",
                (5, 19): "Atatürk'ü Anma, Gençlik ve Spor Bayramı",
                (7, 15): "Demokrasi ve Milli Birlik Günü",
                (8, 30): "Zafer Bayramı",
                (10, 29): "Cumhuriyet Bayramı"
            }
            
            holiday_key = (date_obj.month, date_obj.day)
            if holiday_key in fixed_holidays:
                return True, fixed_holidays[holiday_key]
            
            return False, ""
        except:
            return False, ""
    
    def _get_traffic_explanation(self, city: str, multiplier: float, is_holiday: bool, holiday_name: str) -> str:
        """Trafik durumu açıklaması"""
        if is_holiday:
            if multiplier > 1.5:
                return f"{holiday_name} nedeniyle {city} şehrinde yoğun tatil trafiği bekleniyor"
            elif multiplier < 0.7:
                return f"{holiday_name} nedeniyle {city} şehrinde trafik yoğunluğu azalacak"
            else:
                return f"{holiday_name} nedeniyle {city} şehrinde normal trafik yoğunluğu"
        else:
            if multiplier > 1.5:
                return f"{city} şehrinde yoğun trafik bekleniyor"
            elif multiplier < 0.7:
                return f"{city} şehrinde hafif trafik bekleniyor"
            else:
                return f"{city} şehrinde normal trafik yoğunluğu"
    
    def _get_fallback_predictions(self, cities: List[str], date_str: str) -> Dict:
        """Fallback tahminler"""
        predictions = []
        for city in cities:
            predictions.append({
                "city": city,
                "date": date_str,
                "month": datetime.now().month,
                "season": self._get_season(datetime.now().month),
                "predicted_weather": "güneş",
                "confidence": 0.6,
                "avg_temperature": 15,
                "climate_zone": "Bilinmiyor",
                "traffic_multiplier": 1.0,
                "weather_duration_impact": 1.0,
                "is_holiday": False,
                "holiday_name": "",
                "explanation": f"{city} için varsayılan tahmin",
                "traffic_explanation": f"{city} şehrinde normal trafik yoğunluğu"
            })
        
        return {
            "predictions": predictions,
            "route_summary": {
                "total_cities": len(cities),
                "avg_confidence": 0.6,
                "is_holiday_period": False,
                "holiday_name": "",
                "weather_conditions": ["güneş"],
                "climate_zones": ["Bilinmiyor"],
                "avg_traffic_multiplier": 1.0,
                "total_duration_impact": 1.0
            }
        }
    
    def calculate_route_cost(self, route_distance: float, route_highways: List[str]) -> Dict:
        """Rota maliyeti hesaplama"""
        return self.db.calculate_toll_cost(route_distance, route_highways)
    
    def get_optimal_route_recommendations(self, cities: List[str], date_str: str, 
                                        preferences: Dict = None) -> Dict:
        """Optimal rota önerileri"""
        if not preferences:
            preferences = {
                "priority": "time",  # time, cost, comfort
                "avoid_tolls": False,
                "avoid_mountainous": False,
                "prefer_highways": True
            }
        
        # Hava durumu tahmini
        weather_analysis = self.predict_route_weather(cities, date_str)
        
        # Rota önerileri
        recommendations = {
            "weather_analysis": weather_analysis,
            "route_recommendations": [],
            "cost_analysis": {},
            "traffic_analysis": {},
            "weather_impact": {}
        }
        
        # Hava koşullarına göre öneriler
        weather_conditions = weather_analysis["route_summary"]["weather_conditions"]
        if "kar" in weather_conditions or "karlı" in weather_conditions:
            recommendations["route_recommendations"].append({
                "type": "weather",
                "priority": "high",
                "message": "Karlı hava bekleniyor - Dağlık yolları tercih etmeyin",
                "impact": "duration_increase"
            })
        
        if "yağmur" in weather_conditions or "yağmurlu" in weather_conditions:
            recommendations["route_recommendations"].append({
                "type": "weather",
                "priority": "medium",
                "message": "Yağmurlu hava bekleniyor - Ana yolları tercih edin",
                "impact": "safety_improvement"
            })
        
        # Tatil dönemi önerileri
        if weather_analysis["route_summary"]["is_holiday_period"]:
            recommendations["route_recommendations"].append({
                "type": "holiday",
                "priority": "high",
                "message": f"{weather_analysis['route_summary']['holiday_name']} dönemi - Erken yola çıkın",
                "impact": "traffic_avoidance"
            })
        
        return recommendations

# Flask API entegrasyonu
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

predictor = AdvancedWeatherPredictor()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ML-Based Weather Predictor",
        "cities_loaded": len(predictor.db.cities_data),
        "models_loaded": True,  # ML modelleri yüklü
        "features": [
            "ML tabanlı hava durumu tahmini",
            "Coğrafi veri analizi",
            "Trafik yoğunluğu tahmini",
            "Optimal rota önerileri"
        ]
    })

@app.route('/predict_route', methods=['POST'])
def predict_route_weather():
    try:
        data = request.json
        cities = data.get('cities', [])
        date = data.get('date', '')
        user_weather_conditions = data.get('user_weather_conditions', [])
        
        if not cities or not date:
            return jsonify({'error': 'Şehirler listesi ve tarih gerekli'}), 400
        
        result = predictor.predict_route_weather(cities, date, user_weather_conditions)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/route_recommendations', methods=['POST'])
def get_route_recommendations():
    try:
        data = request.json
        cities = data.get('cities', [])
        date = data.get('date', '')
        preferences = data.get('preferences', {})
        
        if not cities or not date:
            return jsonify({'error': 'Şehirler listesi ve tarih gerekli'}), 400
        
        result = predictor.get_optimal_route_recommendations(cities, date, preferences)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculate_cost', methods=['POST'])
def calculate_route_cost():
    try:
        data = request.json
        distance = data.get('distance', 0)
        highways = data.get('highways', [])
        
        result = predictor.calculate_route_cost(distance, highways)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 ML Tabanlı Hava Durumu Tahmin API'si başlatılıyor...")
    print("📍 Port: 5001")
    print("🔗 Endpoints:")
    print("  - GET  /health")
    print("  - POST /predict_route")
    print("  - POST /route_recommendations")
    print("  - POST /calculate_cost")
    app.run(host='0.0.0.0', port=5001, debug=True) 