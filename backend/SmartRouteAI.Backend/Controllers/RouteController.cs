using Microsoft.AspNetCore.Mvc;
using Services;

namespace SmartRouteAI.Backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class RouteController : ControllerBase
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

        [HttpGet("health")]
        public IActionResult Health()
        {
            return Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
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
            catch (Exception ex)
            {
                Console.WriteLine($"[ANALYZE-PROMPT] Error: {ex.Message}");
                return BadRequest(new { error = "Prompt analizi sırasında hata oluştu" });
            }
        }

        [HttpPost("plan")]
        public async Task<IActionResult> PlanRoute([FromBody] PromptRequest request)
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
    }

    public class PromptRequest
    {
        public string Prompt { get; set; } = string.Empty;
    }
} 