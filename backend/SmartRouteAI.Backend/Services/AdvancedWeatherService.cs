using System.Text.Json;
using System.Text;

namespace Services
{
    public class AdvancedWeatherService
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<AdvancedWeatherService> _logger;
        private readonly string _mlServiceUrl;

        public AdvancedWeatherService(IHttpClientFactory httpClientFactory, ILogger<AdvancedWeatherService> logger, IConfiguration config)
        {
            _httpClient = httpClientFactory.CreateClient();
            _logger = logger;
            _mlServiceUrl = config["MLService:Url"] ?? "http://localhost:5001";
        }

        public class WeatherPrediction
        {
            public string City { get; set; } = string.Empty;
            public string Date { get; set; } = string.Empty;
            public int Month { get; set; }
            public string Season { get; set; } = string.Empty;
            [System.Text.Json.Serialization.JsonPropertyName("predicted_weather")]
            public string PredictedWeather { get; set; } = string.Empty;
            public double Confidence { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("avg_temperature")]
            public double AvgTemperature { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("climate_zone")]
            public string ClimateZone { get; set; } = string.Empty;
            [System.Text.Json.Serialization.JsonPropertyName("traffic_multiplier")]
            public double TrafficMultiplier { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("weather_duration_impact")]
            public double WeatherDurationImpact { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("is_holiday")]
            public bool IsHoliday { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("holiday_name")]
            public string HolidayName { get; set; } = string.Empty;
            public string Explanation { get; set; } = string.Empty;
            [System.Text.Json.Serialization.JsonPropertyName("traffic_explanation")]
            public string TrafficExplanation { get; set; } = string.Empty;
        }

        public class RouteSummary
        {
            public int TotalCities { get; set; }
            public double AvgConfidence { get; set; }
            public bool IsHolidayPeriod { get; set; }
            public string HolidayName { get; set; } = string.Empty;
            public List<string> WeatherConditions { get; set; } = new();
            public List<string> ClimateZones { get; set; } = new();
            public double AvgTrafficMultiplier { get; set; }
            public double TotalDurationImpact { get; set; }
        }

        public class RouteRecommendation
        {
            public string Type { get; set; } = string.Empty;
            public string Priority { get; set; } = string.Empty;
            public string Message { get; set; } = string.Empty;
            public string Impact { get; set; } = string.Empty;
        }

        public class AdvancedWeatherResponse
        {
            public List<WeatherPrediction> Predictions { get; set; } = new();
            public RouteSummary RouteSummary { get; set; } = new();
        }

        public class RouteRecommendationsResponse
        {
            public AdvancedWeatherResponse WeatherAnalysis { get; set; } = new();
            public List<RouteRecommendation> RouteRecommendations { get; set; } = new();
            public Dictionary<string, object> CostAnalysis { get; set; } = new();
            public Dictionary<string, object> TrafficAnalysis { get; set; } = new();
            public Dictionary<string, object> WeatherImpact { get; set; } = new();
        }

        public async Task<AdvancedWeatherResponse> GetAdvancedWeatherPredictionsAsync(List<string> cities, string date, List<string> userWeatherConditions = null)
        {
            try
            {
                _logger.LogInformation($"[WEATHER] Gelişmiş hava durumu tahmini isteniyor: {string.Join(", ", cities)} - {date}");
                _logger.LogInformation($"[WEATHER] ML Service URL: {_mlServiceUrl}");
                if (userWeatherConditions?.Any() == true)
                {
                    _logger.LogInformation($"[WEATHER] Kullanıcı hava durumu koşulları: {string.Join(", ", userWeatherConditions)}");
                }

                var requestData = new
                {
                    cities = cities,
                    date = date,
                    user_weather_conditions = userWeatherConditions ?? new List<string>()
                };

                var json = JsonSerializer.Serialize(requestData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                _logger.LogInformation($"[WEATHER] Request JSON: {json}");

                var response = await _httpClient.PostAsync($"{_mlServiceUrl}/predict_route", content);
                
                _logger.LogInformation($"[WEATHER] Response status: {response.StatusCode}");
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    _logger.LogInformation($"[WEATHER] Response content: {responseContent}");
                    
                    // Response'u detaylı logla
                    _logger.LogInformation($"[WEATHER] Response length: {responseContent.Length}");
                    if (responseContent.Length > 0)
                    {
                        _logger.LogInformation($"[WEATHER] Response starts with: {responseContent.Substring(0, Math.Min(200, responseContent.Length))}");
                    }
                    
                    var result = JsonSerializer.Deserialize<AdvancedWeatherResponse>(responseContent, new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    });

                    _logger.LogInformation($"[WEATHER] Gelişmiş hava durumu tahmini başarılı: {result?.Predictions.Count} şehir");
                    return result ?? new AdvancedWeatherResponse();
                }
                else
                {
                    _logger.LogWarning($"[WEATHER] ML servisi yanıt vermedi: {response.StatusCode}");
                    return await GetFallbackWeatherPredictionsAsync(cities, date);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"[WEATHER] Gelişmiş hava durumu tahmini hatası: {ex.Message}");
                return await GetFallbackWeatherPredictionsAsync(cities, date);
            }
        }

        public async Task<RouteRecommendationsResponse> GetRouteRecommendationsAsync(List<string> cities, string date, Dictionary<string, object> preferences = null)
        {
            try
            {
                _logger.LogInformation($"[RECOMMENDATIONS] Rota önerileri isteniyor: {string.Join(", ", cities)} - {date}");

                var requestData = new
                {
                    cities = cities,
                    date = date,
                    preferences = preferences ?? new Dictionary<string, object>()
                };

                var json = JsonSerializer.Serialize(requestData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"{_mlServiceUrl}/route_recommendations", content);
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<RouteRecommendationsResponse>(responseContent, new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    });

                    _logger.LogInformation($"[RECOMMENDATIONS] Rota önerileri başarılı: {result?.RouteRecommendations.Count} öneri");
                    return result ?? new RouteRecommendationsResponse();
                }
                else
                {
                    _logger.LogWarning($"[RECOMMENDATIONS] ML servisi yanıt vermedi: {response.StatusCode}");
                    return new RouteRecommendationsResponse();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"[RECOMMENDATIONS] Rota önerileri hatası: {ex.Message}");
                return new RouteRecommendationsResponse();
            }
        }

        public async Task<Dictionary<string, object>> CalculateRouteCostAsync(double distance, List<string> highways)
        {
            try
            {
                _logger.LogInformation($"[COST] Rota maliyeti hesaplanıyor: {distance}km, {string.Join(", ", highways)}");

                var requestData = new
                {
                    distance = distance,
                    highways = highways
                };

                var json = JsonSerializer.Serialize(requestData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"{_mlServiceUrl}/calculate_cost", content);
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<Dictionary<string, object>>(responseContent, new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    });

                    _logger.LogInformation($"[COST] Rota maliyeti hesaplandı: {result?.GetValueOrDefault("total_cost")} TL");
                    return result ?? new Dictionary<string, object>();
                }
                else
                {
                    _logger.LogWarning($"[COST] ML servisi yanıt vermedi: {response.StatusCode}");
                    return new Dictionary<string, object>();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"[COST] Rota maliyeti hesaplama hatası: {ex.Message}");
                return new Dictionary<string, object>();
            }
        }

        private async Task<AdvancedWeatherResponse> GetFallbackWeatherPredictionsAsync(List<string> cities, string date)
        {
            _logger.LogInformation($"[FALLBACK] Varsayılan hava durumu tahminleri kullanılıyor");

            var predictions = new List<WeatherPrediction>();
            var currentMonth = DateTime.Now.Month;

            foreach (var city in cities)
            {
                var prediction = new WeatherPrediction
                {
                    City = city,
                    Date = date,
                    Month = currentMonth,
                    Season = GetSeason(currentMonth),
                    PredictedWeather = GetDefaultWeather(city, currentMonth),
                    Confidence = 0.6,
                    AvgTemperature = 15,
                    ClimateZone = "Bilinmiyor",
                    TrafficMultiplier = 1.0,
                    WeatherDurationImpact = 1.0,
                    IsHoliday = false,
                    HolidayName = "",
                    Explanation = $"{city} için varsayılan tahmin",
                    TrafficExplanation = $"{city} şehrinde normal trafik yoğunluğu"
                };

                predictions.Add(prediction);
            }

            return new AdvancedWeatherResponse
            {
                Predictions = predictions,
                RouteSummary = new RouteSummary
                {
                    TotalCities = cities.Count,
                    AvgConfidence = 0.6,
                    IsHolidayPeriod = false,
                    HolidayName = "",
                    WeatherConditions = predictions.Select(p => p.PredictedWeather).Distinct().ToList(),
                    ClimateZones = predictions.Select(p => p.ClimateZone).Distinct().ToList(),
                    AvgTrafficMultiplier = 1.0,
                    TotalDurationImpact = 1.0
                }
            };
        }

        private string GetSeason(int month)
        {
            return month switch
            {
                12 or 1 or 2 => "kış",
                3 or 4 or 5 => "ilkbahar",
                6 or 7 or 8 => "yaz",
                _ => "sonbahar"
            };
        }

        private string GetDefaultWeather(string city, int month)
        {
            var cityLower = city.ToLower();
            
            // Doğu Anadolu
            if (cityLower.Contains("kars") || cityLower.Contains("erzurum") || cityLower.Contains("ağrı") || cityLower.Contains("van"))
            {
                return month is 12 or 1 or 2 ? "kar" : "güneş";
            }
            
            // Karadeniz
            if (cityLower.Contains("trabzon") || cityLower.Contains("rize") || cityLower.Contains("ordu") || cityLower.Contains("sinop"))
            {
                return "yağmur";
            }
            
            // Akdeniz
            if (cityLower.Contains("antalya") || cityLower.Contains("mersin") || cityLower.Contains("adana") || cityLower.Contains("muğla"))
            {
                return "güneş";
            }
            
            // Güneydoğu Anadolu
            if (cityLower.Contains("diyarbakır") || cityLower.Contains("mardin") || cityLower.Contains("batman") || cityLower.Contains("şanlıurfa"))
            {
                return month is 12 or 1 or 2 ? "yağmur" : "güneş";
            }
            
            // Varsayılan
            return month is 6 or 7 or 8 or 9 ? "güneş" : "yağmur";
        }

        public async Task<bool> IsMLServiceHealthyAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_mlServiceUrl}/health");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }
    }
} 