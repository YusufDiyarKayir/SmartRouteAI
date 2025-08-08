using System.Text.Json;
using System.Text;

namespace SmartRouteAI.Backend.Services
{
    public class AIModelService
    {
        private readonly HttpClient _httpClient;
        private readonly string _aiServiceUrl;
        private readonly bool _useSimpleAI;
        private readonly ILogger<AIModelService> _logger;

        public AIModelService(IHttpClientFactory httpClientFactory, IConfiguration config, ILogger<AIModelService> logger)
        {
            _httpClient = httpClientFactory.CreateClient();
            _aiServiceUrl = Environment.GetEnvironmentVariable("ML_SERVICE_URL") ?? "http://localhost:5001";
            _useSimpleAI = config.GetValue<bool>("AIService:UseSimpleAI", true);
            _logger = logger;
        }

        public async Task<AITrafficPrediction> PredictTrafficAsync(RouteInfo routeInfo, WeatherData weatherData, DateTime dateTime)
        {
            try
            {
                var request = new
                {
                    route_info = new
                    {
                        distance = routeInfo.Distance,
                        city_population = routeInfo.CityPopulation,
                        road_quality = routeInfo.RoadQuality,
                        highway_ratio = routeInfo.HighwayRatio
                    },
                    weather_data = new
                    {
                        condition = weatherData.Condition,
                        temperature = weatherData.Temperature,
                        humidity = weatherData.Humidity,
                        wind_speed = weatherData.WindSpeed
                    },
                    date_time = dateTime.ToString("yyyy-MM-ddTHH:mm:ss")
                };

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"{_aiServiceUrl}/predict_traffic", content);
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var prediction = JsonSerializer.Deserialize<AITrafficPrediction>(responseContent);
                    
                    _logger.LogInformation($"AI Traffic Prediction: {prediction.TrafficMultiplier:F2}x (Confidence: {prediction.Confidence:F2})");
                    return prediction;
                }
                else
                {
                    _logger.LogWarning($"AI service error: {response.StatusCode}");
                    return GetFallbackTrafficPrediction(routeInfo, weatherData, dateTime);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"AI traffic prediction error: {ex.Message}");
                return GetFallbackTrafficPrediction(routeInfo, weatherData, dateTime);
            }
        }

        public async Task<AIRouteOptimization> OptimizeRouteAsync(RouteInfo routeInfo, WeatherData weatherData, TrafficData trafficData, UserPreferences userPreferences)
        {
            try
            {
                var request = new
                {
                    route_info = new
                    {
                        distance = routeInfo.Distance,
                        estimated_duration = routeInfo.EstimatedDuration,
                        road_quality = routeInfo.RoadQuality,
                        toll_roads = routeInfo.TollRoads,
                        highway_ratio = routeInfo.HighwayRatio,
                        city_density = routeInfo.CityDensity,
                        hour = routeInfo.Hour,
                        day_of_week = routeInfo.DayOfWeek,
                        is_holiday = routeInfo.IsHoliday
                    },
                    weather_data = new
                    {
                        condition = weatherData.Condition,
                        temperature = weatherData.Temperature,
                        humidity = weatherData.Humidity,
                        wind_speed = weatherData.WindSpeed
                    },
                    traffic_data = new
                    {
                        multiplier = trafficData.Multiplier,
                        level = trafficData.Level
                    },
                    user_preferences = new
                    {
                        duration_weight = userPreferences.DurationWeight,
                        cost_weight = userPreferences.CostWeight,
                        comfort_weight = userPreferences.ComfortWeight
                    }
                };

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"{_aiServiceUrl}/optimize_route", content);
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var optimization = JsonSerializer.Deserialize<AIRouteOptimization>(responseContent);
                    
                    _logger.LogInformation($"AI Route Optimization: Duration={optimization.OptimizedDuration:F1}min, Cost={optimization.EstimatedCost:F0}TL (Score: {optimization.OptimizationScore:F2})");
                    return optimization;
                }
                else
                {
                    _logger.LogWarning($"AI service error: {response.StatusCode}");
                    return GetFallbackRouteOptimization(routeInfo, weatherData, trafficData, userPreferences);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"AI route optimization error: {ex.Message}");
                return GetFallbackRouteOptimization(routeInfo, weatherData, trafficData, userPreferences);
            }
        }

        public async Task<List<AlternativeRoute>> GenerateAlternativeRoutesAsync(string origin, string destination, int numAlternatives = 3)
        {
            try
            {
                var request = new
                {
                    origin = origin,
                    destination = destination,
                    num_alternatives = numAlternatives
                };

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"{_aiServiceUrl}/generate_alternatives", content);
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<AlternativeRoutesResponse>(responseContent);
                    
                    _logger.LogInformation($"AI generated {result.Count} alternative routes");
                    return result.Alternatives;
                }
                else
                {
                    _logger.LogWarning($"AI service error: {response.StatusCode}");
                    return GetFallbackAlternativeRoutes(origin, destination, numAlternatives);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"AI alternative routes error: {ex.Message}");
                return GetFallbackAlternativeRoutes(origin, destination, numAlternatives);
            }
        }

        public async Task<AIModelInfo> GetModelInfoAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync($"{_aiServiceUrl}/model_info");
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var modelInfo = JsonSerializer.Deserialize<AIModelInfo>(responseContent);
                    return modelInfo;
                }
                else
                {
                    return new AIModelInfo
                    {
                        ModelsLoaded = false,
                        TrafficModel = new TrafficModelInfo { Type = "Unknown", Loaded = false },
                        RouteModel = new RouteModelInfo { Type = "Unknown", Loaded = false }
                    };
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"AI model info error: {ex.Message}");
                return new AIModelInfo
                {
                    ModelsLoaded = false,
                    TrafficModel = new TrafficModelInfo { Type = "Error", Loaded = false },
                    RouteModel = new RouteModelInfo { Type = "Error", Loaded = false }
                };
            }
        }

        private AITrafficPrediction GetFallbackTrafficPrediction(RouteInfo routeInfo, WeatherData weatherData, DateTime dateTime)
        {
            var baseMultiplier = 1.0;
            
            // Zaman etkisi
            var hour = dateTime.Hour;
            if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19))
            {
                baseMultiplier *= 1.3; // Rush hour
            }
            
            // Hafta sonu etkisi
            if (dateTime.DayOfWeek == DayOfWeek.Saturday || dateTime.DayOfWeek == DayOfWeek.Sunday)
            {
                baseMultiplier *= 1.2;
            }
            
            // Hava durumu etkisi
            var condition = weatherData.Condition?.ToLower();
            if (condition?.Contains("yağmur") == true)
            {
                baseMultiplier *= 1.1;
            }
            else if (condition?.Contains("kar") == true)
            {
                baseMultiplier *= 1.2;
            }
            
            return new AITrafficPrediction
            {
                TrafficMultiplier = baseMultiplier,
                Confidence = 0.6,
                ModelUsed = "Rule_Based"
            };
        }

        private AIRouteOptimization GetFallbackRouteOptimization(RouteInfo routeInfo, WeatherData weatherData, TrafficData trafficData, UserPreferences userPreferences)
        {
            var baseDuration = routeInfo.EstimatedDuration;
            var baseCost = 100.0; // Base cost
            
            // Trafik etkisi
            var optimizedDuration = baseDuration * trafficData.Multiplier;
            
            // Hava durumu etkisi
            var condition = weatherData.Condition?.ToLower();
            if (condition?.Contains("yağmur") == true)
            {
                optimizedDuration *= 1.1;
            }
            else if (condition?.Contains("kar") == true)
            {
                optimizedDuration *= 1.2;
            }
            
            // Maliyet hesaplama
            var fuelCost = (routeInfo.Distance / 100.0) * 7.0 * 30.0 * trafficData.Multiplier;
            var totalCost = baseCost + fuelCost;
            
            return new AIRouteOptimization
            {
                OptimizedDuration = optimizedDuration,
                EstimatedCost = totalCost,
                ComfortScore = 0.7,
                OptimizationScore = 0.6,
                Confidence = 0.6,
                ModelUsed = "Rule_Based"
            };
        }

        private List<AlternativeRoute> GetFallbackAlternativeRoutes(string origin, string destination, int numAlternatives)
        {
            var alternatives = new List<AlternativeRoute>();
            
            for (int i = 0; i < numAlternatives; i++)
            {
                var variationFactor = 1.0 + (i * 0.1); // %10 artış
                
                alternatives.Add(new AlternativeRoute
                {
                    RouteId = $"route_{i + 1}",
                    Distance = 100 * variationFactor,
                    EstimatedDuration = 60 * variationFactor,
                    HighwayRatio = 0.3 + (i * 0.1),
                    TollRoads = i % 2,
                    RoadQuality = 0.8 - (i * 0.05)
                });
            }
            
            return alternatives;
        }
    }

    // Data Models
    public class RouteInfo
    {
        public double Distance { get; set; }
        public double EstimatedDuration { get; set; }
        public double CityPopulation { get; set; } = 1000000;
        public double RoadQuality { get; set; } = 0.8;
        public int TollRoads { get; set; } = 0;
        public double HighwayRatio { get; set; } = 0.3;
        public double CityDensity { get; set; } = 0.5;
        public int Hour { get; set; }
        public int DayOfWeek { get; set; }
        public bool IsHoliday { get; set; }
    }

    public class WeatherData
    {
        public string Condition { get; set; } = "";
        public double Temperature { get; set; } = 20;
        public double Humidity { get; set; } = 50;
        public double WindSpeed { get; set; } = 10;
    }

    public class TrafficData
    {
        public double Multiplier { get; set; } = 1.0;
        public double Level { get; set; } = 0.5;
    }

    public class UserPreferences
    {
        public double DurationWeight { get; set; } = 0.4;
        public double CostWeight { get; set; } = 0.3;
        public double ComfortWeight { get; set; } = 0.3;
    }

    public class AITrafficPrediction
    {
        public double TrafficMultiplier { get; set; }
        public double Confidence { get; set; }
        public string ModelUsed { get; set; } = "";
    }

    public class AIRouteOptimization
    {
        public double OptimizedDuration { get; set; }
        public double EstimatedCost { get; set; }
        public double ComfortScore { get; set; }
        public double OptimizationScore { get; set; }
        public double Confidence { get; set; }
        public string ModelUsed { get; set; } = "";
    }

    public class AlternativeRoute
    {
        public string RouteId { get; set; } = "";
        public double Distance { get; set; }
        public double EstimatedDuration { get; set; }
        public double HighwayRatio { get; set; }
        public int TollRoads { get; set; }
        public double RoadQuality { get; set; }
    }

    public class AlternativeRoutesResponse
    {
        public List<AlternativeRoute> Alternatives { get; set; } = new();
        public int Count { get; set; }
    }

    public class AIModelInfo
    {
        public bool ModelsLoaded { get; set; }
        public TrafficModelInfo TrafficModel { get; set; } = new();
        public RouteModelInfo RouteModel { get; set; } = new();
    }

    public class TrafficModelInfo
    {
        public string Type { get; set; } = "";
        public List<string> Features { get; set; } = new();
        public bool Loaded { get; set; }
    }

    public class RouteModelInfo
    {
        public string Type { get; set; } = "";
        public List<string> Features { get; set; } = new();
        public bool Loaded { get; set; }
    }
} 