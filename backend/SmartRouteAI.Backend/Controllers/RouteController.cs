using Microsoft.AspNetCore.Mvc;
using SmartRouteAI.Backend.Models;
using SmartRouteAI.Backend.Services;

namespace SmartRouteAI.Backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class RouteController : ControllerBase
{
    private readonly RouteOptimizationService _routeService;
    private readonly AdvancedWeatherService _weatherService;
    private readonly HolidayService _holidayService;
    private readonly PromptAnalysisService _promptService;

    public RouteController(
        RouteOptimizationService routeService,
        AdvancedWeatherService weatherService,
        HolidayService holidayService,
        PromptAnalysisService promptService)
    {
        _routeService = routeService;
        _weatherService = weatherService;
        _holidayService = holidayService;
        _promptService = promptService;
    }

    [HttpPost("estimate")]
    public async Task<IActionResult> GetRouteEstimate([FromBody] RouteRequest request)
    {
        try
        {
            var dt = DateTime.Parse($"{request.Date}T{request.Time}");
            var epoch = ((DateTimeOffset)dt).ToUnixTimeSeconds();

            // Tatil kontrolü
            var isHoliday = await _holidayService.IsHolidayAsync(dt);

            // Hava durumu bilgisi
            var weatherInfo = await _weatherService.GetWeatherInfoAsync(request.FromLat, request.FromLng, dt);

            // Trafik yoğunluğu tahmini
            var trafficLevel = GetTrafficLevel(dt);

            // Google Directions API ile rota hesaplama
            var routes = await GetRoutesFromGoogleAsync(request, epoch, dt, weatherInfo.Description);

            return Ok(new
            {
                routes,
                date = request.Date,
                time = request.Time,
                isHoliday,
                weather = weatherInfo.Condition,
                trafficLevel
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    [HttpGet("test")]
    public IActionResult Test()
    {
        return Ok(new { message = "Route controller çalışıyor!" });
    }

    [HttpPost("analyze-prompt")]
    public async Task<IActionResult> AnalyzePrompt([FromBody] PromptRequest request)
    {
        try
        {
            Console.WriteLine($"[ROUTE] AnalyzePrompt çağrıldı. Prompt: {request.Prompt}");
            
            // Prompt analizi yap
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
            Console.WriteLine($"[ROUTE] AnalyzePrompt hatası: {ex.Message}");
            return BadRequest(new { error = ex.Message });
        }
    }

    [HttpPost("plan")]
    public async Task<IActionResult> PlanRoute([FromBody] PromptRequest request)
    {
        try
        {
            Console.WriteLine($"[ROUTE] PlanRoute çağrıldı. Prompt: {request.Prompt}");
            
            // Prompt analizi yap
            var analysis = await _promptService.AnalyzePromptAsync(request.Prompt);
            Console.WriteLine($"[ROUTE] Analysis tamamlandı. Source: {analysis.Source}, Destination: {analysis.Destination}");
            
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
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[HOLIDAY] Error parsing date: {ex.Message}");
                }
            }

            // Rota optimizasyonu yap
            var results = await _routeService.OptimizeRouteAsync(
                analysis.Source,
                analysis.Destination,
                analysis.Route.Skip(1).Take(analysis.Route.Count - 2).ToList(),
                analysis.Requests,
                analysis.BridgeDirectives,
                analysis.HighwayDirectives,
                analysis.WeatherConditions,
                analysis.TravelDate,
                analysis.TravelTime
            );

            // Yanıt formatını frontend'e uygun hale getir
            var response = results.Select(r => new {
                route = r.Route,
                polyline = r.Polyline,
                distanceKm = r.DistanceKm,
                durationMin = r.DurationMin,
                adjustedDurationMin = r.AdjustedDurationMin,
                summary = r.Summary,
                hasToll = r.HasToll,
                weatherImpact = r.WeatherImpact
            }).ToList();

            var result = new {
                alternatives = response,
                requests = analysis.Requests,
                constraints = new List<string>(),
                weatherPredictions = new List<object>(),
                routeRecommendations = new List<object>(),
                costAnalysis = new Dictionary<string, object>(),
                routeSummary = new {
                    totalCities = analysis.Route.Count,
                    isHolidayPeriod = false,
                    holidayName = "",
                    avgTrafficMultiplier = 1.0,
                    totalDurationImpact = 1.0,
                    mlPredictionsCount = 0,
                    weatherConditions = new List<string>()
                },
                mlServiceUsed = false,
                trafficMultipliers = new List<double>(),
                holidayInfo = holidayInfo
            };
            
            Console.WriteLine($"[ROUTE] Yanıt hazırlandı. Alternatives count: {response.Count}");
            return Ok(result);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ROUTE] Hata: {ex.Message}");
            Console.WriteLine($"[ROUTE] Stack trace: {ex.StackTrace}");
            return BadRequest(new { error = ex.Message });
        }
    }

    private string GetTrafficLevel(DateTime dt)
    {
        var hour = dt.Hour;
        var dayOfWeek = dt.DayOfWeek;

        if (dayOfWeek == DayOfWeek.Saturday || dayOfWeek == DayOfWeek.Sunday)
            return "Low";
        
        if (hour >= 7 && hour <= 10 || hour >= 17 && hour <= 20)
            return "High";
        
        if (hour >= 11 && hour <= 16)
            return "Medium";
        
        return "Low";
    }

    private async Task<List<object>> GetRoutesFromGoogleAsync(RouteRequest request, long epoch, DateTime dt, string weatherDesc)
    {
        var routes = new List<object>();
        var googleApiKey = Environment.GetEnvironmentVariable("GOOGLE_MAPS_API_KEY") ?? "";
        
        var googleUrl = $"https://maps.googleapis.com/maps/api/directions/json?" +
                       $"origin={request.FromLat.ToString(System.Globalization.CultureInfo.InvariantCulture)},{request.FromLng.ToString(System.Globalization.CultureInfo.InvariantCulture)}" +
                       $"&destination={request.ToLat.ToString(System.Globalization.CultureInfo.InvariantCulture)},{request.ToLng.ToString(System.Globalization.CultureInfo.InvariantCulture)}" +
                       $"&departure_time={epoch}&alternatives=true&key={googleApiKey}";

        try
        {
            using var http = new HttpClient();
            var googleResp = await http.GetStringAsync(googleUrl);
            var googleObj = System.Text.Json.JsonSerializer.Deserialize<GoogleDirectionsResponse>(googleResp);

            if (googleObj?.routes.Length > 0)
            {
                var (minDurationIdx, minTollIdx) = FindOptimalRoutes(googleObj.routes);
                routes = ProcessRoutes(googleObj.routes, minDurationIdx, minTollIdx, dt, weatherDesc);
            }
        }
        catch (Exception ex)
        {
            routes.Add(new { title = "Hata", distanceKm = 0, estimatedDurationMinutes = 0, polyline = "", tollClass = "-", error = ex.Message });
        }

        return routes;
    }

    private (int minDurationIdx, int minTollIdx) FindOptimalRoutes(GoogleRoute[] routes)
    {
        int minDurationIdx = 0, minTollIdx = 0;
        int minDuration = int.MaxValue, minToll = int.MaxValue;

        for (int i = 0; i < routes.Length; i++)
        {
            var r = routes[i];
            var leg = r.legs[0];
            double durationMin = leg.duration_in_traffic?.value / 60.0 ?? leg.duration.value / 60.0;
            int tollCount = CountTolls(leg.steps);

            if (durationMin < minDuration) { minDuration = (int)durationMin; minDurationIdx = i; }
            if (tollCount < minToll) { minToll = tollCount; minTollIdx = i; }
        }

        return (minDurationIdx, minTollIdx);
    }

    private int CountTolls(GoogleStep[] steps)
    {
        if (steps == null) return 0;

        return steps.Count(step => 
            step.html_instructions?.ToLower().Contains("toll") == true || 
            step.html_instructions?.ToLower().Contains("ücretli") == true);
    }

    private List<object> ProcessRoutes(GoogleRoute[] routes, int minDurationIdx, int minTollIdx, DateTime dt, string weatherDesc)
    {
        var processedRoutes = new List<object>();

        for (int i = 0; i < routes.Length; i++)
        {
            var r = routes[i];
            var leg = r.legs[0];
            double distanceKm = leg.distance.value / 1000.0;
            double durationMin = leg.duration_in_traffic?.value / 60.0 ?? leg.duration.value / 60.0;
            string polyline = r.overview_polyline.points;

            int tollCount = CountTolls(leg.steps);
            string tollClass = GetTollClass(tollCount);
            string tollInfo = tollCount == 0 ? "Ücretsiz rota" : $"Tahmini {tollCount} adet ücretli geçiş olabilir.";

            string title = $"Alternatif {i + 1}";
            if (i == minDurationIdx) title += " - En hızlı";
            if (i == minTollIdx) title += " - En düşük maliyetli";
            if (tollCount == 0) title += " - Ücretsiz";

            var arrival = dt.AddMinutes(durationMin);
            string arrivalStr = arrival.ToString("dd MMMM yyyy HH:mm", new System.Globalization.CultureInfo("tr-TR"));

            processedRoutes.Add(new
            {
                title,
                distanceKm = Math.Round(distanceKm, 2),
                estimatedDurationMinutes = Math.Round(durationMin, 1),
                polyline,
                tollClass,
                tollCount,
                tollInfo,
                arrivalStr,
                weatherDesc
            });
        }

        return processedRoutes;
    }

    private string GetTollClass(int tollCount)
    {
        return tollCount switch
        {
            0 => "Ücretsiz",
            1 or 2 => "Orta",
            _ => "Yüksek"
        };
    }
} 