using System.Text.Json;
using System.Text;
using SmartRouteAI.Backend.Models;

namespace SmartRouteAI.Backend.Services
{
    public class AdvancedWeatherService
    {
        private readonly HttpClient _httpClient; //HTTP istekleri için kullanılan HttpClient
        private readonly ILogger<AdvancedWeatherService> _logger; //Loglama için kullanılan ILogger
        private readonly string _mlServiceUrl; //ML servis URL

        public AdvancedWeatherService(IHttpClientFactory httpClientFactory, ILogger<AdvancedWeatherService> logger, IConfiguration config) //HttpClientFactory, ILogger ve IConfiguration parametreleri alan constructor
        {
            _httpClient = httpClientFactory.CreateClient(); //HttpClient oluştur
            _logger = logger; //Logger'ı atama
            _mlServiceUrl = config["MLService:Url"] ?? "http://localhost:5001"; //ML servis URL'yi atama
        }

        public class WeatherPrediction //Hava durumu tahmini için kullanılan sınıf
        {
            public string City { get; set; } = string.Empty;
            public string Date { get; set; } = string.Empty;
            public int Month { get; set; }
            public string Season { get; set; } = string.Empty;
            [System.Text.Json.Serialization.JsonPropertyName("predicted_weather")] //Tahmin edilen hava durumu JSON serilizasyonu için kullanılan JsonPropertyName
            public string PredictedWeather { get; set; } = string.Empty;
            public double Confidence { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("avg_temperature")] //Ortalama sıcaklık JSON serilizasyonu için kullanılan JsonPropertyName
            public double AvgTemperature { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("climate_zone")] //iklim bölgesi JSON serilizasyonu için kullanılan JsonPropertyName
            public string ClimateZone { get; set; } = string.Empty;
            [System.Text.Json.Serialization.JsonPropertyName("traffic_multiplier")] //trafik çarpanı JSON serilizasyonu için kullanılan JsonPropertyName
            public double TrafficMultiplier { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("weather_duration_impact")] //Hava durumu süresi çarpanı JSON serilizasyonu için kullanılan JsonPropertyName
            public double WeatherDurationImpact { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("is_holiday")] //Tatil kontrolü JSON serilizasyonu için kullanılan JsonPropertyName
            public bool IsHoliday { get; set; }
            [System.Text.Json.Serialization.JsonPropertyName("holiday_name")] //Tatil adı JSON serilizasyonu için kullanılan JsonPropertyName
            public string HolidayName { get; set; } = string.Empty;
            public string Explanation { get; set; } = string.Empty;
            [System.Text.Json.Serialization.JsonPropertyName("traffic_explanation")] //Trafik açıklaması JSON serilizasyonu için kullanılan JsonPropertyName
            public string TrafficExplanation { get; set; } = string.Empty;
        }

        public class RouteSummary
        {
            public int TotalCities { get; set; } 
            public double AvgConfidence { get; set; }
            public bool IsHolidayPeriod { get; set; }
            public string HolidayName { get; set; } = string.Empty;
            public List<string> WeatherConditions { get; set; } = new(); //Hava durumu koşulları
            public List<string> ClimateZones { get; set; } = new(); //İklim bölgeleri
            public double AvgTrafficMultiplier { get; set; } //Ortalama trafik çarpanı
            public double TotalDurationImpact { get; set; } //Toplam süre etkisi
        }

        public class RouteRecommendation //Rota önerisi
        {
            public string Type { get; set; } = string.Empty; //Rota tipi
            public string Priority { get; set; } = string.Empty; //Öncelik
            public string Message { get; set; } = string.Empty; //Mesaj
            public string Impact { get; set; } = string.Empty; //Etkisi
        }

        public class AdvancedWeatherResponse //Hava durumu yanıtı
        {
            public List<WeatherPrediction> Predictions { get; set; } = new(); //Hava durumu tahminleri
            public RouteSummary RouteSummary { get; set; } = new(); //Rota özeti
        }

        public class RouteRecommendationsResponse //Rota önerileri yanıtı
        {
            public AdvancedWeatherResponse WeatherAnalysis { get; set; } = new(); //Hava durumu analizi
            public List<RouteRecommendation> RouteRecommendations { get; set; } = new(); //Rota önerileri
            public Dictionary<string, object> CostAnalysis { get; set; } = new(); //Maliyet analizi
            public Dictionary<string, object> TrafficAnalysis { get; set; } = new(); //Trafik analizi
            public Dictionary<string, object> WeatherImpact { get; set; } = new(); //Hava durumu etkisi
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

                // Python ML servisinde /route_recommendations endpoint'i yok, 
                // bu yüzden basit bir fallback response döndürüyoruz
                var recommendations = new List<RouteRecommendation>();
                
                // Hava durumu tahmini al
                var weatherResponse = await GetAdvancedWeatherPredictionsAsync(cities, date);
                
                if (weatherResponse?.Predictions?.Any() == true)
                {
                    var weatherConditions = weatherResponse.Predictions.Select(p => p.PredictedWeather).Distinct().ToList();
                    
                    // Hava koşullarına göre öneriler
                    if (weatherConditions.Any(w => w.Contains("kar") || w.Contains("karlı")))
                    {
                        recommendations.Add(new RouteRecommendation
                        {
                            Type = "weather",
                            Priority = "high",
                            Message = "Karlı hava bekleniyor - Dağlık yolları tercih etmeyin",
                            Impact = "duration_increase"
                        });
                    }
                    
                    if (weatherConditions.Any(w => w.Contains("yağmur") || w.Contains("yağmurlu")))
                    {
                        recommendations.Add(new RouteRecommendation
                        {
                            Type = "weather",
                            Priority = "medium",
                            Message = "Yağmurlu hava bekleniyor - Ana yolları tercih edin",
                            Impact = "safety_improvement"
                        });
                    }
                    
                    // Tatil dönemi önerileri
                    if (weatherResponse.RouteSummary.IsHolidayPeriod)
                    {
                        recommendations.Add(new RouteRecommendation
                        {
                            Type = "holiday",
                            Priority = "high",
                            Message = $"{weatherResponse.RouteSummary.HolidayName} dönemi - Erken yola çıkın",
                            Impact = "traffic_avoidance"
                        });
                    }
                }

                _logger.LogInformation($"[RECOMMENDATIONS] Rota önerileri oluşturuldu: {recommendations.Count} öneri");
                
                return new RouteRecommendationsResponse
                {
                    WeatherAnalysis = weatherResponse ?? new AdvancedWeatherResponse(),
                    RouteRecommendations = recommendations,
                    CostAnalysis = new Dictionary<string, object>(),
                    TrafficAnalysis = new Dictionary<string, object>(),
                    WeatherImpact = new Dictionary<string, object>()
                };
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

        public async Task<(string Condition, string Description)> GetWeatherInfoAsync(double lat, double lng, DateTime dt)
        {
            try
            {
                string weatherApiKey = Environment.GetEnvironmentVariable("OPENWEATHER_API_KEY") ?? "";
                string forecastUrl = $"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lng}&appid={weatherApiKey}&lang=tr&units=metric";
                
                var forecastResp = await _httpClient.GetFromJsonAsync<OpenWeatherForecastResponse>(forecastUrl);
                if (forecastResp?.list.Length > 0)
                {
                    var closest = forecastResp.list.OrderBy(x => Math.Abs((DateTimeOffset.FromUnixTimeSeconds(x.dt).DateTime - dt).TotalMinutes)).First();
                    var main = closest.weather[0].main.ToLower();
                    var description = closest.weather[0].description;

                    var condition = main switch
                    {
                        var w when w.IndexOf("rain", StringComparison.OrdinalIgnoreCase) >= 0 => "Rainy",
                        var w when w.IndexOf("snow", StringComparison.OrdinalIgnoreCase) >= 0 => "Snowy",
                        var w when w.IndexOf("cloud", StringComparison.OrdinalIgnoreCase) >= 0 => "Cloudy",
                        _ => "Sunny"
                    };

                    return (condition, description);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Hava durumu bilgisi alınırken hata oluştu");
            }

            return ("Sunny", "");
        }
    }
} 