using Microsoft.AspNetCore.Mvc;
using Services;
using SmartRouteAI.Backend.Models;

namespace SmartRouteAI.Backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
        
    public class RouteController : ControllerBase       //RouteController sınıfı
    {
        private readonly PromptAnalysisService _promptService; 
        private readonly RouteOptimizationService _routeService; 
        private readonly MapService _mapService;
        private readonly AdvancedWeatherService _advancedWeatherService;
        private readonly HolidayService _holidayService;
        
        public RouteController(PromptAnalysisService promptService, RouteOptimizationService routeService, MapService mapService, AdvancedWeatherService advancedWeatherService, HolidayService holidayService)
        {
            _promptService = promptService;
            _routeService = routeService;
            _mapService = mapService;
            _advancedWeatherService = advancedWeatherService;
            _holidayService = holidayService;

        }

        [HttpGet("health")]// Sağlık kontrolü endpoint'i
        public IActionResult Health() //Sağlık kontrolü
        {
            return Ok(new { status = "healthy", timestamp = DateTime.UtcNow }); //Sağlık kontrolü
        }

        [HttpPost("analyze-prompt")]
        public async Task<IActionResult> AnalyzePrompt([FromBody] PromptRequest request)
        {
            try
            {
                var analysis = await _promptService.AnalyzePromptAsync(request.Prompt);
                
                return Ok(new
                {
                    source = analysis.Source,
                    destination = analysis.Destination,
                    requests = analysis.Requests,
                    bridgeDirectives = analysis.BridgeDirectives,
                    highwayDirectives = analysis.HighwayDirectives,
                    weatherConditions = analysis.WeatherConditions,
                    travelDate = analysis.TravelDate,
                    travelTime = analysis.TravelTime,
                    route = analysis.Route
                });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Sizi anlayamadım"))
            {
                Console.WriteLine($"[ANALYZE-PROMPT] Anlamsız prompt: {ex.Message}");
                return BadRequest(new { 
                    error = ex.Message,
                    type = "meaningless_prompt",
                    suggestion = "Lütfen geçerli bir rota isteği girin. Örnek: 'İstanbul'dan Ankara'ya git' veya 'Bursa'dan İzmir'e yolculuk'"
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ANALYZE-PROMPT] Error: {ex.Message}");
                return BadRequest(new { error = "Prompt analizi sırasında hata oluştu" });
            }
        }

        [HttpPost("plan")]
        public async Task<IActionResult> PlanRoute([FromBody] PromptRequest request)
        {
            try
            {
                var analysis = await _promptService.AnalyzePromptAsync(request.Prompt);
                
                // Tatil kontrolü
                var holidayInfo = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(analysis.TravelDate))
                {
                    try
                    {
                        var travelDate = DateTime.Parse(analysis.TravelDate);
                        var holiday = _holidayService.CheckHoliday(travelDate);
                        var trafficMultiplier = _holidayService.GetTrafficMultiplier(travelDate);
                        var holidayImpact = _holidayService.GetHolidayImpact(travelDate);
                        
                        holidayInfo = new Dictionary<string, object>
                        {
                            ["isHoliday"] = holiday != null,
                            ["holidayName"] = holiday?.Name ?? "Tatil günü değil",
                            ["holidayType"] = holiday?.Type ?? "",
                            ["trafficMultiplier"] = trafficMultiplier,
                            ["holidayImpact"] = holidayImpact,
                            ["dayOfWeek"] = travelDate.DayOfWeek.ToString(),
                            ["isWeekend"] = travelDate.DayOfWeek == DayOfWeek.Saturday || travelDate.DayOfWeek == DayOfWeek.Sunday
                        };
                        
                        Console.WriteLine($"[HOLIDAY] Date: {analysis.TravelDate}, Holiday: {holiday?.Name ?? "None"}, Traffic Multiplier: {trafficMultiplier}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[HOLIDAY] Error parsing date: {ex.Message}");
                    }
                }
                
                // ML tabanlı hava durumu tahmini
                var mlWeatherPredictions = new List<object>();
                var routeRecommendations = new List<object>();
                var costAnalysis = new Dictionary<string, object>();
                var weatherConditions = new List<string>();
                var trafficMultipliers = new List<double>();
                
                Console.WriteLine($"[CONTROLLER] Analysis.TravelDate: '{analysis.TravelDate}'");
                Console.WriteLine($"[CONTROLLER] Analysis.Route.Count: {analysis.Route.Count}");
                Console.WriteLine($"[CONTROLLER] Analysis.Route: [{string.Join(", ", analysis.Route)}]");
                
                if (!string.IsNullOrEmpty(analysis.TravelDate) && analysis.Route.Count > 0)
                {
                    try
                    {
                        Console.WriteLine($"[CONTROLLER] ML Service çağrılıyor - Route: {string.Join(", ", analysis.Route)}, Date: {analysis.TravelDate}");
                        
                        // ML servisinden hava durumu tahmini al
                        var mlPredictions = await _advancedWeatherService.GetAdvancedWeatherPredictionsAsync(analysis.Route, analysis.TravelDate, analysis.WeatherConditions);
                        
                        Console.WriteLine($"[CONTROLLER] ML Service yanıtı alındı - Predictions count: {mlPredictions?.Predictions?.Count ?? 0}");
                        
                        if (mlPredictions?.Predictions?.Any() == true)
                        {
                            Console.WriteLine($"[CONTROLLER] ML tahminleri işleniyor...");
                            Console.WriteLine($"[CONTROLLER] ML Predictions count: {mlPredictions.Predictions.Count}");
                            
                            // Her tahmin için detaylı log
                            foreach (var pred in mlPredictions.Predictions)
                            {
                                Console.WriteLine($"[CONTROLLER] Prediction: {pred.City} -> Weather:'{pred.PredictedWeather}', Temp:{pred.AvgTemperature}, Confidence:{pred.Confidence}");
                            }
                            
                            mlWeatherPredictions = mlPredictions.Predictions.Select(p => new {
                                city = p.City,
                                date = p.Date,
                                season = p.Season,
                                predictedWeather = p.PredictedWeather,
                                confidence = p.Confidence,
                                avgTemperature = p.AvgTemperature,
                                climateZone = p.ClimateZone,
                                trafficMultiplier = p.TrafficMultiplier,
                                weatherDurationImpact = p.WeatherDurationImpact,
                                isHoliday = p.IsHoliday,
                                holidayName = p.HolidayName,
                                explanation = p.Explanation,
                                trafficExplanation = p.TrafficExplanation
                            }).ToList<object>();
                            
                            // ML tahminlerinden hava koşullarını ve trafik çarpanlarını al
                            var allWeathers = mlPredictions.Predictions.Select(p => p.PredictedWeather).ToList();
                            Console.WriteLine($"[CONTROLLER] All weathers before distinct: [{string.Join("|", allWeathers)}]");
                            
                            // Kullanıcının istediği hava durumu koşullarını öncelik ver
                            if (analysis.WeatherConditions.Any())
                            {
                                weatherConditions = analysis.WeatherConditions;
                                Console.WriteLine($"[CONTROLLER] Using user-requested weather conditions: {string.Join(", ", weatherConditions)}");
                            }
                            else
                            {
                                weatherConditions = allWeathers.Distinct().ToList();
                                Console.WriteLine($"[CONTROLLER] Using ML-predicted weather conditions: {string.Join(", ", weatherConditions)}");
                            }
                            
                            trafficMultipliers = mlPredictions.Predictions.Select(p => p.TrafficMultiplier).ToList();
                            
                            Console.WriteLine($"[CONTROLLER] Weather conditions: {string.Join(", ", weatherConditions)}");
                            Console.WriteLine($"[CONTROLLER] Traffic multipliers: {string.Join(", ", trafficMultipliers)}");
                            Console.WriteLine($"[CONTROLLER] Weather conditions count: {weatherConditions.Count}");
                            Console.WriteLine($"[CONTROLLER] Weather conditions content: [{string.Join("|", weatherConditions)}]");
                            
                            // Rota önerileri
                            var recommendations = await _advancedWeatherService.GetRouteRecommendationsAsync(analysis.Route, analysis.TravelDate);
                            routeRecommendations = recommendations.RouteRecommendations.Select(r => new {
                                type = r.Type,
                                priority = r.Priority,
                                message = r.Message,
                                impact = r.Impact
                            }).ToList<object>();
                            
                            // Maliyet analizi
                            if (analysis.Route.Count > 1)
                            {
                                var estimatedDistance = analysis.Route.Count * 100.0; // Tahmini mesafe
                                var highways = analysis.HighwayDirectives.Where(h => h.Use).Select(h => h.Name).ToList();
                                costAnalysis = await _advancedWeatherService.CalculateRouteCostAsync(estimatedDistance, highways);
                            }
                        }
                        else
                        {
                            Console.WriteLine($"[CONTROLLER] ML Service boş yanıt döndü veya null");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[CONTROLLER] ML Weather Service error: {ex.Message}");
                        Console.WriteLine($"[CONTROLLER] Stack trace: {ex.StackTrace}");
                    }
                }
                else
                {
                    Console.WriteLine($"[CONTROLLER] ML Service çağrılmadı - TravelDate: {analysis.TravelDate}, Route count: {analysis.Route.Count}");
                }
                
                // ML tahminlerini kullanarak rota optimizasyonu yap
                Console.WriteLine($"[CONTROLLER] Calling OptimizeRouteAsync with weatherConditions: [{string.Join("|", weatherConditions)}]");
                
                var results = await _routeService.OptimizeRouteAsync(
                    analysis.Source,
                    analysis.Destination,
                    analysis.Route.Skip(1).Take(analysis.Route.Count - 2).ToList(),
                    analysis.Requests,
                    analysis.BridgeDirectives,
                    analysis.HighwayDirectives,
                    weatherConditions, // ML'den gelen hava koşulları
                    analysis.TravelDate,
                    analysis.TravelTime
                );
                
                // Her rota için mapUrl üret
                var mapUrls = results.Select(r => _mapService.GetMapUrlAsync(r.Route)).ToArray();
                await Task.WhenAll(mapUrls);
                
                var response = results.Select((r, i) => new {
                    route = r.Route,
                    polyline = r.Polyline,
                    distanceKm = r.DistanceKm,
                    durationMin = r.DurationMin,
                    adjustedDurationMin = r.AdjustedDurationMin,
                    summary = r.Summary,
                    hasToll = r.HasToll,
                    weatherImpact = r.WeatherImpact,
                    mapUrl = mapUrls[i].Result
                }).ToList();
                
                // Kısıtlamaları frontend'e ilet
                var constraints = new List<string>();
                constraints.AddRange(analysis.BridgeDirectives.Select(b => b.Use ? $"{b.Name} köprüsünü kullan" : $"{b.Name} köprüsünü kullanma"));
                constraints.AddRange(analysis.HighwayDirectives.Select(h => h.Use ? $"{h.Name} otoyolunu kullan" : $"{h.Name} otoyolunu kullanma"));
                
                // Route summary hesaplama
                var routeSummary = new
                {
                    totalCities = analysis.Route.Count,
                    isHolidayPeriod = false,
                    holidayName = "",
                    avgTrafficMultiplier = 1.0,
                    totalDurationImpact = 1.0,
                    mlPredictionsCount = 0,
                    weatherConditions = new List<string>()
                };
                
                // ML tahminlerinden route summary'yi güncelle
                if (mlWeatherPredictions.Any())
                {
                    try
                    {
                        var firstPrediction = mlWeatherPredictions.First();
                        var properties = firstPrediction.GetType().GetProperties();
                        
                        var isHolidayProp = properties.FirstOrDefault(p => p.Name == "isHoliday");
                        var holidayNameProp = properties.FirstOrDefault(p => p.Name == "holidayName");
                        var trafficMultiplierProp = properties.FirstOrDefault(p => p.Name == "trafficMultiplier");
                        var weatherDurationImpactProp = properties.FirstOrDefault(p => p.Name == "weatherDurationImpact");
                        
                        var isHoliday = isHolidayProp?.GetValue(firstPrediction) as bool? ?? false;
                        var holidayName = holidayNameProp?.GetValue(firstPrediction) as string ?? "";
                        var avgTrafficMultiplier = trafficMultiplierProp?.GetValue(firstPrediction) as double? ?? 1.0;
                        var totalDurationImpact = weatherDurationImpactProp?.GetValue(firstPrediction) as double? ?? 1.0;
                        
                        // ML tahminlerinden ortalama trafik çarpanını hesapla
                        if (trafficMultipliers.Any())
                        {
                            avgTrafficMultiplier = trafficMultipliers.Average();
                        }
                        
                        routeSummary = new
                        {
                            totalCities = analysis.Route.Count,
                            isHolidayPeriod = isHoliday,
                            holidayName = holidayName,
                            avgTrafficMultiplier = avgTrafficMultiplier,
                            totalDurationImpact = totalDurationImpact,
                            mlPredictionsCount = mlWeatherPredictions.Count,
                            weatherConditions = weatherConditions
                        };
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[CONTROLLER] ML Route summary calculation error: {ex.Message}");
                    }
                }
                
                return Ok(new {
                    alternatives = response,
                    requests = analysis.Requests,
                    constraints,
                    weatherPredictions = mlWeatherPredictions, // ML tahminleri
                    routeRecommendations = routeRecommendations,
                    costAnalysis = costAnalysis,
                    routeSummary = routeSummary,
                    mlServiceUsed = mlWeatherPredictions.Any(),
                    trafficMultipliers = trafficMultipliers,
                    holidayInfo = holidayInfo // Tatil bilgileri
                });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Sizi anlayamadım"))
            {
                Console.WriteLine($"[PLAN-ROUTE] Anlamsız prompt: {ex.Message}");
                return BadRequest(new { 
                    error = ex.Message,
                    type = "meaningless_prompt",
                    suggestion = "Lütfen geçerli bir rota isteği girin. Örnek: 'İstanbul'dan Ankara'ya git' veya 'Bursa'dan İzmir'e yolculuk'"
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[PLAN-ROUTE] Error: {ex.Message}");
                return BadRequest(new { error = "Rota planlama sırasında hata oluştu" });
            }
        }

        [HttpPost("estimate")]
        public async Task<IActionResult> GetRouteEstimate([FromBody] RouteRequest request)
        {
            // Koordinatlar ve zaman bilgileri alınıyor
            double fromLat = request.FromLat; 
            double fromLng = request.FromLng;
            double toLat = request.ToLat;
            double toLng = request.ToLng;
            string date = request.Date;
            string time = request.Time;

            var dt = DateTime.Parse($"{date}T{time}"); // Tarih + saat birleştiriliyor
            var epoch = ((DateTimeOffset)dt).ToUnixTimeSeconds(); // UNIX zamanına çevrilir

            // 1. Tatil kontrolü: Abstract API kullanılarak
            bool isHoliday = false; // Tatil kontrolü
            try {
                using var http = new HttpClient(); // HTTP isteği oluşturuluyor
                string holidayApiKey = Environment.GetEnvironmentVariable("HOLIDAY_API_KEY") ?? "";
                string holidayUrl = $"https://holidays.abstractapi.com/v1/?api_key={holidayApiKey}&country=TR&year={dt.Year}&month={dt.Month}&day={dt.Day}";
                var holidayResp = await http.GetStringAsync(holidayUrl); // Abstract API'den gelen yanıt
                isHoliday = !string.IsNullOrWhiteSpace(holidayResp) && holidayResp != "[]"; // Yanıt boş değilse ve [] değilse tatil kontrolü
            } catch { } // Hata olursa tatil kontrolü yapılmaz

            // 2. Hava durumu bilgisi: OpenWeatherMap API üzerinden
            string weather = "Sunny";
            string weatherDesc = ""; // Hava durumu açıklaması
            try {
                using var http = new HttpClient(); // HTTP isteği oluşturuluyor
                string weatherApiKey = Environment.GetEnvironmentVariable("OPENWEATHER_API_KEY") ?? ""; // OpenWeatherMap API anahtarı
                string forecastUrl = $"https://api.openweathermap.org/data/2.5/forecast?lat={fromLat}&lon={fromLng}&appid={weatherApiKey}&lang=tr&units=metric"; // OpenWeatherMap API URL'si
                var forecastResp = await http.GetFromJsonAsync<OpenWeatherForecastResponse>(forecastUrl); // OpenWeatherMap API'den gelen yanıt
                if (forecastResp != null && forecastResp.list.Length > 0) {
                    // En yakın tarihli hava verisi seçiliyor
                    var closest = forecastResp.list.OrderBy(x => Math.Abs((DateTimeOffset.FromUnixTimeSeconds(x.dt).DateTime - dt).TotalMinutes)).First();
                    var main = closest.weather[0].main.ToLower();
                    weatherDesc = closest.weather[0].description;

                    // Hava durumu sınıflandırması yapılıyor
                    if (main.Contains("rain")) weather = "Rainy";
                    else if (main.Contains("snow")) weather = "Snowy";
                    else if (main.Contains("cloud")) weather = "Cloudy";
                    else weather = "Sunny";
                }
            } catch { }

            // 3. Trafik yoğunluğu tahmini
            string trafficLevel = "Low";
            int hour = dt.Hour;
            var dayOfWeek = dt.DayOfWeek;
            if (dayOfWeek == DayOfWeek.Saturday || dayOfWeek == DayOfWeek.Sunday) {
                trafficLevel = "Low"; // Hafta sonu düşük
            } else if (hour >= 7 && hour <= 10) trafficLevel = "High"; // Sabah yoğun saatler
            else if (hour >= 17 && hour <= 20) trafficLevel = "High"; // Akşam yoğun saatler
            else if (hour >= 11 && hour <= 16) trafficLevel = "Medium"; // Orta yoğunluk

            // 4. Google Directions API üzerinden güzergahlar alınıyor
            string googleApiKey = Environment.GetEnvironmentVariable("GOOGLE_MAPS_API_KEY") ?? "";
            string googleUrl = $"https://maps.googleapis.com/maps/api/directions/json?origin={fromLat.ToString(System.Globalization.CultureInfo.InvariantCulture)},{fromLng.ToString(System.Globalization.CultureInfo.InvariantCulture)}&destination={toLat.ToString(System.Globalization.CultureInfo.InvariantCulture)},{toLng.ToString(System.Globalization.CultureInfo.InvariantCulture)}&departure_time={epoch}&alternatives=true&key={googleApiKey}";
            
            Console.WriteLine("[GOOGLE URL] " + googleUrl); // Konsola URL yazdır

            var routes = new List<object>(); // Rota listesi

            try
            {
                using var http = new HttpClient();
                var googleResp = await http.GetStringAsync(googleUrl);
                Console.WriteLine("[GOOGLE RESP] " + googleResp);

                var googleObj = System.Text.Json.JsonSerializer.Deserialize<GoogleDirectionsResponse>(googleResp);
                if (googleObj != null && googleObj.routes.Length > 0)
                {
                    // En hızlı ve en az ücretli rota seçimi
                    int minDurationIdx = 0; // En hızlı rota indeksi
                    int minTollIdx = 0; // En az ücretli rota indeksi
                    int minDuration = int.MaxValue; // En hızlı rota süresi
                    int minToll = int.MaxValue; // En az ücretli rota ücreti

                    // Güzergahları kontrol et
                    for (int i = 0; i < googleObj.routes.Length; i++) // Güzergahları kontrol et
                    {
                        var r = googleObj.routes[i]; // Güzergah
                        var leg = r.legs[0]; // Güzergahın ilk adımı
                        double durationMin = leg.duration_in_traffic != null ? leg.duration_in_traffic.value / 60.0 : leg.duration.value / 60.0; // Güzergahın süresi
                        int tollCount = 0; // Ücretli geçiş sayısı

                        if (leg.steps != null) // Adımlar varsa
                        {
                            foreach (var step in leg.steps) // Adımları kontrol et
                            {
                                if (step.html_instructions != null && (step.html_instructions.ToLower().Contains("toll") || step.html_instructions.ToLower().Contains("ücretli"))) // Ücretli geçiş varsa
                                    tollCount++; // Ücretli geçiş sayısını artır
                            }
                        }

                        if (durationMin < minDuration) { minDuration = (int)durationMin; minDurationIdx = i; }
                        if (tollCount < minToll) { minToll = tollCount; minTollIdx = i; }
                    }

                    // Güzergahları listeye ekle
                    for (int i = 0; i < googleObj.routes.Length; i++)
                    {
                        var r = googleObj.routes[i];
                        var leg = r.legs[0];
                        double distanceKm = leg.distance.value / 1000.0;
                        double durationMin = leg.duration_in_traffic != null ? leg.duration_in_traffic.value / 60.0 : leg.duration.value / 60.0;
                        string polyline = r.overview_polyline.points;

                        int tollCount = 0;
                        if (leg.steps != null)
                        {
                            foreach (var step in leg.steps)
                            {
                                if (step.html_instructions != null)
                                {
                                    var instruction = step.html_instructions.ToLower();
                                    if (instruction.Contains("toll") || 
                                        instruction.Contains("ücretli") || 
                                        instruction.Contains("otoyol") ||
                                        instruction.Contains("highway") ||
                                        instruction.Contains("motorway") ||
                                        instruction.Contains("expressway") ||
                                        instruction.Contains("otoban") ||
                                        instruction.Contains("geçiş") ||
                                        instruction.Contains("köprü") ||
                                        instruction.Contains("tünel"))
                                    {
                                        tollCount++;
                                    }
                                }
                            }
                        }

                        string tollClass = "Ücretsiz";
                        if (tollCount == 1 || tollCount == 2) tollClass = "Orta";
                        else if (tollCount >= 3) tollClass = "Yüksek";
                        string tollInfo = tollCount == 0 ? "Ücretsiz rota" : $"Tahmini {tollCount} adet ücretli geçiş olabilir.";
                        

                        string title = $"Alternatif {i+1}";
                        if (i == minDurationIdx) title += " - En hızlı";
                        if (i == minTollIdx) title += " - En düşük maliyetli";
                        if (tollCount == 0) title += " - Ücretsiz";

                        var arrival = dt.AddMinutes(durationMin);
                        string arrivalStr = arrival.ToString("dd MMMM yyyy HH:mm", new System.Globalization.CultureInfo("tr-TR"));

                        var routeData = new {
                            title,
                            distanceKm = Math.Round(distanceKm, 2),
                            estimatedDurationMinutes = Math.Round(durationMin, 1),
                            polyline,
                            tollClass,
                            tollCount,
                            tollInfo,
                            arrivalStr,
                            weatherDesc
                        };
                        

                        routes.Add(routeData);
                    }
                }
            }
            catch (Exception ex)
            {
                // Hata olursa varsayılan rota döndür
                routes.Clear();
                routes.Add(new { title = "Hata", distanceKm = 0, estimatedDurationMinutes = 0, polyline = "", tollClass = "-", error = ex.Message });
            }

            // Sonuçlar JSON olarak döndürülüyor
            return Ok(new
            {
                routes,
                date,
                time,
                isHoliday,
                weather,
                trafficLevel
            });
        }
    }

} 