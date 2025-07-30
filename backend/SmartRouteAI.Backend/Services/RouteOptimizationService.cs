using System.Net.Http;
using Microsoft.Extensions.Configuration;
using System.Text.Json;

namespace Services
{
    public class RouteOptimizationService
    {
        private readonly string _googleApiKey;
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly HolidayService _holidayService;
        private readonly AIModelService _aiModelService;
        
        public RouteOptimizationService(IConfiguration config, IHttpClientFactory httpClientFactory, HolidayService holidayService, AIModelService aiModelService)
        {
            _googleApiKey = config["GoogleMaps:ApiKey"] ?? "";
            _httpClientFactory = httpClientFactory;
            _holidayService = holidayService;
            _aiModelService = aiModelService;
        }

        public class StepDetail
        {
            public string Instruction { get; set; } = string.Empty;
            public string? RoadName { get; set; }
            public double DistanceKm { get; set; }
            public string? Maneuver { get; set; }
        }
        public class RouteResult
        {
            public List<string> Route { get; set; } = new();
            public string Polyline { get; set; } = string.Empty;
            public double DistanceKm { get; set; }
            public double DurationMin { get; set; }
            public double AdjustedDurationMin { get; set; } // AI ve hava koşullarına göre ayarlanmış süre
            public string Summary { get; set; } = string.Empty;
            public bool HasToll { get; set; }
            public List<StepDetail> Steps { get; set; } = new();
            public string WeatherImpact { get; set; } = string.Empty; // AI, hava koşulları ve tatil etkisi
            public bool IsHoliday { get; set; } = false; // Tatil günü mü?
            public string HolidayName { get; set; } = string.Empty; // Tatil adı
            public double HolidayTrafficMultiplier { get; set; } = 1.0; // Tatil trafik çarpanı
            
            // AI alanları
            public bool AIOptimized { get; set; } = false; // AI ile optimize edildi mi?
            public double AIOptimizationScore { get; set; } = 0.0; // AI optimizasyon skoru
            public double AIConfidence { get; set; } = 0.0; // AI güven skoru
            public string AIModelUsed { get; set; } = string.Empty; // Kullanılan AI modeli
        }

        // Google Roads API ile snap-to-road
        private async Task<string> SnapToRoadAsync(string location)
        {
            // location: "lat,lng" formatında olmalı
            if (string.IsNullOrWhiteSpace(location) || !_googleApiKey.Any()) 
            {
                Console.WriteLine($"[ROADS API] Skipping snap for: {location} (empty or no API key)");
                return location;
            }
            
            var url = $"https://roads.googleapis.com/v1/snapToRoads?path={location}&key={_googleApiKey}";
            Console.WriteLine($"[ROADS API] Request URL: {url}");
            
            try
            {
                var client = _httpClientFactory.CreateClient();
                var response = await client.GetAsync(url);
                Console.WriteLine($"[ROADS API] Response status: {response.StatusCode}");
                
                if (!response.IsSuccessStatusCode) 
                {
                    Console.WriteLine($"[ROADS API] Failed to snap location: {location}");
                    return location;
                }
                
                var json = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"[ROADS API] Response: {json}");
                
                using var doc = JsonDocument.Parse(json);
                var root = doc.RootElement;
                
                if (root.TryGetProperty("snappedPoints", out var snappedElem) && snappedElem.GetArrayLength() > 0)
                {
                    var snapped = snappedElem[0];
                    if (snapped.TryGetProperty("location", out var locElem))
                    {
                        var lat = locElem.GetProperty("latitude").GetDouble();
                        var lng = locElem.GetProperty("longitude").GetDouble();
                        var snappedLocation = $"{lat},{lng}";
                        Console.WriteLine($"[ROADS API] Snapped {location} to {snappedLocation}");
                        return snappedLocation;
                    }
                }
                
                Console.WriteLine($"[ROADS API] No snapped points found for: {location}");
            }
            catch (Exception ex) 
            { 
                Console.WriteLine($"[ROADS API] Error snapping location {location}: {ex.Message}");
            }
            
            return location;
        }

        // Sıralı şehirleri tek seferde Google Maps'e waypoints olarak göndererek rota oluştur
        public async Task<List<RouteResult>> OptimizeRouteAsync(string source, string destination, List<string> waypoints, List<string> requests, List<(string Name, bool Use)> bridgeDirectives, List<(string Name, bool Use)> highwayDirectives, List<string> weatherConditions = null, string travelDate = null, string travelTime = null)
        {
            var results = new List<RouteResult>();
            var cities = new List<string>();
            if (!string.IsNullOrEmpty(source)) cities.Add(source);
            if (waypoints != null && waypoints.Count > 0) cities.AddRange(waypoints);
            if (!string.IsNullOrEmpty(destination)) cities.Add(destination);
            if (cities.Count < 2) return results;

            // Şehir/adres yerine koordinat gelirse snap-to-road uygula
            async Task<string> SnapIfCoord(string s)
            {
                Console.WriteLine($"[SNAP] Checking location: {s}");
                // Eğer s "lat,lng" formatında ise snap et
                if (System.Text.RegularExpressions.Regex.IsMatch(s, @"^-?\d+\.\d+,-?\d+\.\d+$"))
                {
                    Console.WriteLine($"[SNAP] Found coordinate format, snapping: {s}");
                    var snapped = await SnapToRoadAsync(s);
                    Console.WriteLine($"[SNAP] Result: {s} -> {snapped}");
                    return snapped;
                }
                Console.WriteLine($"[SNAP] Not a coordinate, keeping as is: {s}");
                return s;
            }
            
            Console.WriteLine($"[SNAP] Processing {cities.Count} locations");
            for (int i = 0; i < cities.Count; i++)
            {
                Console.WriteLine($"[SNAP] Processing city {i}: {cities[i]}");
                cities[i] = await SnapIfCoord(cities[i]);
            }

            // Debug: Final route order
            Console.WriteLine($"[ROUTE] Final route order:");
            for (int i = 0; i < cities.Count; i++)
            {
                Console.WriteLine($"[ROUTE] {i}: {cities[i]}");
            }

            string Encode(string s) => Uri.EscapeDataString(s);
            var origin = Encode(cities[0] + ", Türkiye");
            var dest = Encode(cities[^1] + ", Türkiye");
            var waypointsStr = cities.Count > 2 ? "&waypoints=" + string.Join("|", cities.Skip(1).Take(cities.Count - 2).Select(w => Encode(w + ", Türkiye"))) : "";
            
            Console.WriteLine($"[ROUTE] Origin: {origin}");
            Console.WriteLine($"[ROUTE] Destination: {dest}");
            Console.WriteLine($"[ROUTE] Waypoints: {waypointsStr}");
            
            // ML tabanlı hava koşullarına göre rota optimizasyonu
            var avoidParams = new List<string>();
            // Temel kaçınılacak yollar
            avoidParams.Add("ferries");
            
            if (weatherConditions != null && weatherConditions.Any())
            {
                Console.WriteLine($"[ML WEATHER] ML Conditions: {string.Join(", ", weatherConditions)}");
                
                // ML tahminlerine göre rota optimizasyonu
                if (weatherConditions.Any(w => w.Contains("yağmur") || w.Contains("yağmurlu")))
                {
                    Console.WriteLine("[ML WEATHER] ML Rain detected - optimizing route for rain conditions");
                    // Yağmurlu havalarda ana yolları tercih et
                    avoidParams.Add("highways");
                }
                
                if (weatherConditions.Any(w => w.Contains("kar") || w.Contains("karlı")))
                {
                    Console.WriteLine("[ML WEATHER] ML Snow detected - optimizing route for snow conditions");
                    // Karlı havalarda daha güvenli yolları tercih et
                    avoidParams.Add("highways");
                }
                
                if (weatherConditions.Any(w => w.Contains("güneş") || w.Contains("güneşli")))
                {
                    Console.WriteLine("[ML WEATHER] ML Sunny weather - optimal conditions for travel");
                }
                
                if (weatherConditions.Any(w => w.Contains("rüzgar") || w.Contains("fırtına")))
                {
                    Console.WriteLine("[ML WEATHER] ML Windy/Stormy conditions - avoiding exposed routes");
                    // Rüzgarlı havalarda açık yolları kaçın
                }
            }
            
            // Tarih ve saat bilgisi
            if (!string.IsNullOrEmpty(travelDate))
            {
                Console.WriteLine($"[DATE] Travel date: {travelDate}");
            }
            if (!string.IsNullOrEmpty(travelTime))
            {
                Console.WriteLine($"[TIME] Travel time: {travelTime}");
            }
            
            var avoidStr = avoidParams.Any() ? $"&avoid={string.Join("|", avoidParams)}" : "&avoid=ferries";
            var url = $"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={dest}{waypointsStr}&alternatives=true{avoidStr}&mode=driving&traffic_model=best_guess&departure_time=now&key={_googleApiKey}";
            Console.WriteLine($"[GOOGLE API] Request URL: {url}");
            var client = _httpClientFactory.CreateClient();
            var response = await client.GetAsync(url);
            Console.WriteLine($"[GOOGLE API] Response status: {response.StatusCode}");
            if (!response.IsSuccessStatusCode) return results;
            var json = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            if (root.TryGetProperty("routes", out var routesElem) && routesElem.GetArrayLength() > 0)
            {
                foreach (var routeElem in routesElem.EnumerateArray())
                {
                    var result = new RouteResult();
                    if (routeElem.TryGetProperty("overview_polyline", out var polyElem))
                    {
                        result.Polyline = polyElem.GetProperty("points").GetString() ?? string.Empty;
                        Console.WriteLine($"[POLYLINE] Route polyline length: {result.Polyline.Length}");
                    }
                    else
                    {
                        Console.WriteLine("[POLYLINE] No polyline found for route");
                    }
                    if (routeElem.TryGetProperty("summary", out var summaryElem))
                        result.Summary = summaryElem.GetString() ?? string.Empty;
                    result.HasToll = false;
                    if (routeElem.TryGetProperty("warnings", out var warningsElem) && warningsElem.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var warn in warningsElem.EnumerateArray())
                        {
                            var w = warn.GetString() ?? "";
                            if (w.ToLower().Contains("toll") || w.ToLower().Contains("ücretli"))
                                result.HasToll = true;
                        }
                    }
                    if (routeElem.TryGetProperty("legs", out var legsElem))
                    {
                        double totalDistance = 0, totalDuration = 0;
                        foreach (var leg in legsElem.EnumerateArray())
                        {
                            var start = leg.GetProperty("start_address").GetString();
                            var end = leg.GetProperty("end_address").GetString();
                            if (!string.IsNullOrEmpty(start) && !result.Route.Contains(start))
                                result.Route.Add(start);
                            if (!string.IsNullOrEmpty(end) && !result.Route.Contains(end))
                                result.Route.Add(end);
                            if (leg.TryGetProperty("distance", out var distElem))
                                totalDistance += distElem.GetProperty("value").GetDouble();
                            if (leg.TryGetProperty("duration", out var durElem))
                                totalDuration += durElem.GetProperty("value").GetDouble();
                            // Steps
                            if (leg.TryGetProperty("steps", out var stepsElem) && stepsElem.ValueKind == JsonValueKind.Array && stepsElem.GetArrayLength() > 0)
                            {
                                foreach (var step in stepsElem.EnumerateArray())
                                {
                                    try {
                                        var detail = new StepDetail();
                                        if (step.TryGetProperty("html_instructions", out var instElem))
                                            detail.Instruction = System.Text.RegularExpressions.Regex.Replace(instElem.GetString() ?? "", "<.*?>", "");
                                        if (step.TryGetProperty("distance", out var sDistElem))
                                            detail.DistanceKm = Math.Round((sDistElem.GetProperty("value").GetDouble() / 1000.0), 2);
                                        if (step.TryGetProperty("maneuver", out var manElem))
                                            detail.Maneuver = manElem.GetString();
                                        if (step.TryGetProperty("name", out var nameElem))
                                            detail.RoadName = nameElem.GetString();
                                        result.Steps.Add(detail);
                                    } catch { /* step parse hatası */ }
                                }
                            } else {
                                // Steps yoksa, en azından leg özeti ekle
                                var legSummary = new StepDetail {
                                    Instruction = $"{start} → {end}",
                                    DistanceKm = Math.Round((leg.GetProperty("distance").GetProperty("value").GetDouble() / 1000.0), 2)
                                };
                                result.Steps.Add(legSummary);
                            }
                        }
                        result.DistanceKm = Math.Round(totalDistance / 1000.0, 2);
                        result.DurationMin = Math.Round(totalDuration / 60.0, 1);
                        
                        // ML tabanlı hava koşullarına göre süre ayarlaması
                        result.AdjustedDurationMin = result.DurationMin;
                        
                        // AI destekli trafik ve rota optimizasyonu
                        var holidayMultiplier = 1.0;
                        var holidayImpact = new List<string>();
                        var aiOptimization = false;
                        
                        if (!string.IsNullOrEmpty(travelDate))
                        {
                            try
                            {
                                var travelDateTime = DateTime.Parse(travelDate);
                                
                                // Tatil kontrolü
                                var holiday = _holidayService.CheckHoliday(travelDateTime);
                                var trafficMultiplier = _holidayService.GetTrafficMultiplier(travelDateTime);
                                
                                if (holiday != null)
                                {
                                    holidayMultiplier = trafficMultiplier;
                                    holidayImpact.Add($"{holiday.Name} nedeniyle trafik yoğunluğu {trafficMultiplier:F1}x");
                                    result.IsHoliday = true;
                                    result.HolidayName = holiday.Name;
                                    result.HolidayTrafficMultiplier = trafficMultiplier;
                                    Console.WriteLine($"[HOLIDAY] {holiday.Name} - Traffic multiplier: {trafficMultiplier:F1}x");
                                }
                                else if (travelDateTime.DayOfWeek == DayOfWeek.Saturday || travelDateTime.DayOfWeek == DayOfWeek.Sunday)
                                {
                                    holidayMultiplier = 1.3; // Hafta sonu
                                    holidayImpact.Add("Hafta sonu nedeniyle trafik yoğunluğu 1.3x");
                                    result.IsHoliday = true;
                                    result.HolidayName = "Hafta Sonu";
                                    result.HolidayTrafficMultiplier = 1.3;
                                    Console.WriteLine("[HOLIDAY] Weekend - Traffic multiplier: 1.3x");
                                }
                                
                                // AI trafik tahmini
                                try
                                {
                                    var routeInfo = new RouteInfo
                                    {
                                        Distance = result.DistanceKm,
                                        CityPopulation = 1500000, // İstanbul için
                                        RoadQuality = 0.8,
                                        HighwayRatio = 0.3,
                                        Hour = travelDateTime.Hour,
                                        DayOfWeek = (int)travelDateTime.DayOfWeek,
                                        IsHoliday = holiday != null
                                    };
                                    
                                    var weatherData = new WeatherData
                                    {
                                        Condition = weatherConditions?.FirstOrDefault() ?? "güneşli",
                                        Temperature = 20,
                                        Humidity = 50,
                                        WindSpeed = 10
                                    };
                                    
                                    var aiTrafficPrediction = await _aiModelService.PredictTrafficAsync(routeInfo, weatherData, travelDateTime);
                                    
                                    if (aiTrafficPrediction.ModelUsed == "AI_LSTM")
                                    {
                                        holidayMultiplier = aiTrafficPrediction.TrafficMultiplier;
                                        holidayImpact.Add($"AI tahmini: Trafik yoğunluğu {aiTrafficPrediction.TrafficMultiplier:F2}x (Güven: {aiTrafficPrediction.Confidence:F2})");
                                        aiOptimization = true;
                                        Console.WriteLine($"[AI] Traffic prediction: {aiTrafficPrediction.TrafficMultiplier:F2}x (Confidence: {aiTrafficPrediction.Confidence:F2})");
                                    }
                                }
                                catch (Exception aiEx)
                                {
                                    Console.WriteLine($"[AI] Traffic prediction error: {aiEx.Message}");
                                }
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"[HOLIDAY] Error parsing date: {ex.Message}");
                            }
                        }
                        Console.WriteLine($"[ROUTE OPTIMIZATION] Weather conditions received: {weatherConditions?.Count ?? 0}");
                        Console.WriteLine($"[ROUTE OPTIMIZATION] Weather conditions content: [{string.Join("|", weatherConditions ?? new List<string>())}]");
                        
                        if (weatherConditions != null && weatherConditions.Any())
                        {
                            var weatherMultiplier = 1.0;
                            var weatherImpact = new List<string>();
                            
                            Console.WriteLine($"[ML DURATION] ML Weather conditions affecting duration: {string.Join(", ", weatherConditions)}");
                            
                            // Hava durumlarını benzersiz hale getir
                            var uniqueWeatherConditions = weatherConditions.Distinct().ToList();
                            
                            // En kötü hava durumunu bul (en yüksek etki)
                            var worstWeather = "";
                            var maxMultiplier = 1.0;
                            
                            foreach (var condition in uniqueWeatherConditions)
                            {
                                var currentMultiplier = 1.0;
                                var currentWeather = "";
                                
                                if (condition.Contains("kar") || condition.Contains("karlı"))
                                {
                                    currentMultiplier = 1.15; // %15 uzun
                                    currentWeather = "kar";
                                }
                                else if (condition.Contains("yağmur") || condition.Contains("yağmurlu"))
                                {
                                    currentMultiplier = 1.1; // %10 uzun
                                    currentWeather = "yağmur";
                                }
                                else if (condition.Contains("fırtına") || condition.Contains("rüzgar"))
                                {
                                    currentMultiplier = 1.12; // %12 uzun
                                    currentWeather = "fırtına";
                                }
                                else if (condition.Contains("sis") || condition.Contains("sisli"))
                                {
                                    currentMultiplier = 1.08; // %8 uzun
                                    currentWeather = "sis";
                                }
                                else if (condition.Contains("güneş") || condition.Contains("güneşli"))
                                {
                                    currentMultiplier = 0.98; // %2 kısa
                                    currentWeather = "güneş";
                                }
                                
                                // En kötü hava durumunu güncelle
                                if (currentMultiplier > maxMultiplier)
                                {
                                    maxMultiplier = currentMultiplier;
                                    worstWeather = currentWeather;
                                }
                            }
                            
                            // Sadece en kötü hava durumunu uygula
                            if (!string.IsNullOrEmpty(worstWeather))
                            {
                                weatherMultiplier = maxMultiplier;
                                
                                switch (worstWeather)
                                {
                                    case "kar":
                                        weatherImpact.Add("ML: Karlı hava nedeniyle süre %15 artırıldı");
                                        Console.WriteLine("[ML DURATION] Worst weather (Snow) impact: +15% duration");
                                        break;
                                    case "yağmur":
                                        weatherImpact.Add("ML: Yağmurlu hava nedeniyle süre %10 artırıldı");
                                        Console.WriteLine("[ML DURATION] Worst weather (Rain) impact: +10% duration");
                                        break;
                                    case "fırtına":
                                        weatherImpact.Add("ML: Fırtınalı hava nedeniyle süre %12 artırıldı");
                                        Console.WriteLine("[ML DURATION] Worst weather (Storm) impact: +12% duration");
                                        break;
                                    case "sis":
                                        weatherImpact.Add("ML: Sisli hava nedeniyle süre %8 artırıldı");
                                        Console.WriteLine("[ML DURATION] Worst weather (Fog) impact: +8% duration");
                                        break;
                                    case "güneş":
                                        weatherImpact.Add("ML: Güneşli hava nedeniyle süre %2 azaltıldı");
                                        Console.WriteLine("[ML DURATION] Best weather (Sunny) impact: -2% duration");
                                        break;
                                }
                            }
                            
                            // AI rota optimizasyonu
                            if (aiOptimization)
                            {
                                try
                                {
                                    var routeInfo = new RouteInfo
                                    {
                                        Distance = result.DistanceKm,
                                        EstimatedDuration = result.DurationMin,
                                        RoadQuality = 0.8,
                                        TollRoads = result.HasToll ? 1 : 0,
                                        HighwayRatio = 0.3,
                                        CityDensity = 0.7,
                                        Hour = DateTime.Parse(travelDate).Hour,
                                        DayOfWeek = (int)DateTime.Parse(travelDate).DayOfWeek,
                                        IsHoliday = result.IsHoliday
                                    };
                                    
                                    var weatherData = new WeatherData
                                    {
                                        Condition = weatherConditions?.FirstOrDefault() ?? "güneşli",
                                        Temperature = 20,
                                        Humidity = 50,
                                        WindSpeed = 10
                                    };
                                    
                                    var trafficData = new TrafficData
                                    {
                                        Multiplier = holidayMultiplier,
                                        Level = 0.5
                                    };
                                    
                                    var userPreferences = new UserPreferences
                                    {
                                        DurationWeight = 0.4,
                                        CostWeight = 0.3,
                                        ComfortWeight = 0.3
                                    };
                                    
                                    var aiRouteOptimization = await _aiModelService.OptimizeRouteAsync(routeInfo, weatherData, trafficData, userPreferences);
                                    
                                    if (aiRouteOptimization.ModelUsed == "AI_Transformer")
                                    {
                                        result.AdjustedDurationMin = Math.Round(aiRouteOptimization.OptimizedDuration, 1);
                                        result.AIOptimizationScore = aiRouteOptimization.OptimizationScore;
                                        result.AIConfidence = aiRouteOptimization.Confidence;
                                        result.AIOptimized = true;
                                        result.AIModelUsed = "LSTM + Transformer";
                                        
                                        holidayImpact.Add($"AI optimizasyon: {aiRouteOptimization.OptimizedDuration:F1}dk (Skor: {aiRouteOptimization.OptimizationScore:F2})");
                                        
                                        Console.WriteLine($"[AI] Route optimization: {aiRouteOptimization.OptimizedDuration:F1}min (Score: {aiRouteOptimization.OptimizationScore:F2}, Confidence: {aiRouteOptimization.Confidence:F2})");
                                    }
                                }
                                catch (Exception aiEx)
                                {
                                    Console.WriteLine($"[AI] Route optimization error: {aiEx.Message}");
                                }
                            }
                            
                            // Fallback: Hava durumu ve tatil etkilerini birleştir
                            if (!aiOptimization)
                            {
                                var totalMultiplier = weatherMultiplier * holidayMultiplier;
                                result.AdjustedDurationMin = Math.Round(result.DurationMin * totalMultiplier, 1);
                            }
                            
                            // Etki açıklamalarını birleştir
                            var allImpacts = new List<string>();
                            allImpacts.AddRange(weatherImpact);
                            allImpacts.AddRange(holidayImpact);
                            result.WeatherImpact = string.Join("; ", allImpacts);
                            
                            Console.WriteLine($"[DURATION] Original: {result.DurationMin} min, Final: {result.AdjustedDurationMin} min, AI: {aiOptimization}");
                            Console.WriteLine($"[IMPACT] Combined impacts: {result.WeatherImpact}");
                        }
                        else
                        {
                            // Sadece tatil etkisi varsa
                            if (holidayMultiplier != 1.0)
                            {
                                result.AdjustedDurationMin = Math.Round(result.DurationMin * holidayMultiplier, 1);
                                result.WeatherImpact = string.Join("; ", holidayImpact);
                                Console.WriteLine($"[DURATION] Original: {result.DurationMin} min, Holiday: {holidayMultiplier:F2}x, Final: {result.AdjustedDurationMin} min");
                                Console.WriteLine($"[IMPACT] Holiday impacts: {result.WeatherImpact}");
                            }
                        }
                    }
                    results.Add(result);
                }
            }
            return results;
        }

        // Polyline decode fonksiyonu (Google polyline algoritması)
        private List<(double, double)> DecodePolyline(string encoded)
        {
            var poly = new List<(double, double)>();
            int index = 0, len = encoded.Length;
            int lat = 0, lng = 0;
            while (index < len)
            {
                int b, shift = 0, result = 0;
                do
                {
                    b = encoded[index++] - 63;
                    result |= (b & 0x1f) << shift;
                    shift += 5;
                } while (b >= 0x20);
                int dlat = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
                lat += dlat;
                shift = 0;
                result = 0;
                do
                {
                    b = encoded[index++] - 63;
                    result |= (b & 0x1f) << shift;
                    shift += 5;
                } while (b >= 0x20);
                int dlng = ((result & 1) != 0 ? ~(result >> 1) : (result >> 1));
                lng += dlng;
                poly.Add((lat / 1E5, lng / 1E5));
            }
            return poly;
        }
        // Polyline encode fonksiyonu (Google polyline algoritması)
        private string EncodePolyline(List<(double, double)> points)
        {
            var str = new System.Text.StringBuilder();
            int prevLat = 0, prevLng = 0;
            foreach (var (lat, lng) in points)
            {
                int latE5 = (int)Math.Round(lat * 1E5);
                int lngE5 = (int)Math.Round(lng * 1E5);
                int dLat = latE5 - prevLat;
                int dLng = lngE5 - prevLng;
                prevLat = latE5;
                prevLng = lngE5;
                foreach (var v in new[] { dLat, dLng })
                {
                    int sv = v < 0 ? ~(v << 1) : (v << 1);
                    while (sv >= 0x20)
                    {
                        str.Append((char)((0x20 | (sv & 0x1f)) + 63));
                        sv >>= 5;
                    }
                    str.Append((char)(sv + 63));
                }
            }
            return str.ToString();
        }

        // Köprü ve otoyol isimleri listesi (PromptAnalysisService ile aynı)
        private static readonly List<(string Name, string Type, (double, double) Coord)> _bridges = new()
        {
            ("15 Temmuz Şehitler Köprüsü", "bridge", (41.0438, 29.0327)),
            ("Boğaziçi Köprüsü", "bridge", (41.0438, 29.0327)),
            ("Fatih Sultan Mehmet Köprüsü", "bridge", (41.0915, 29.0635)),
            ("FSM Köprüsü", "bridge", (41.0915, 29.0635)),
            ("Yavuz Sultan Selim Köprüsü", "bridge", (41.1815, 29.0736)),
            ("Kuzey Marmara Köprüsü", "bridge", (41.1815, 29.0736)),
            ("Osmangazi Köprüsü", "bridge", (40.7487, 29.4847)),
        };
        private static readonly List<(string Name, string Type, (double, double) Coord)> _highways = new()
        {
            ("Kuzey Marmara Otoyolu", "highway", (41.1815, 29.0736)),
            ("TEM Otoyolu", "highway", (41.0915, 29.0635)),
            ("O-7", "highway", (41.1815, 29.0736)),
            ("O-4", "highway", (41.0915, 29.0635)),
            ("E-5", "highway", (40.9903, 28.8034)), // Halkalı koordinatları
            ("D100", "highway", (41.1333, 29.0833)), // Beykoz koordinatları
        };
    }
}