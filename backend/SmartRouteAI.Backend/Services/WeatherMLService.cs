using System.Text.Json;
using System.Text; //Metin verisi kodlamak için

namespace Services
{
    public class WeatherMLService
    {
        private readonly HttpClient _httpClient;
        private readonly string _mlServiceUrl;
        //ML servisini başlatır
        public WeatherMLService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _mlServiceUrl = configuration["MLService:Url"] ?? "http://localhost:5001"; // Advanced weather servisi
        }

        //Rota için hava durumu tahmini yapar
        public async Task<List<WeatherPrediction>> PredictWeatherForRouteAsync(List<string> cities, string date)
        {
            try
            {
                var requestData = new
                {
                    cities = cities,
                    date = date
                };

                var json = JsonSerializer.Serialize(requestData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                Console.WriteLine($"[HISTORICAL WEATHER] Requesting weather prediction for {cities.Count} cities on {date}");
                Console.WriteLine($"[HISTORICAL WEATHER] Request URL: {_mlServiceUrl}/predict_route");

                var response = await _httpClient.PostAsync($"{_mlServiceUrl}/predict_route", content);
                //ML servisinden yanıt alır
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<WeatherPredictionResponse>(responseContent);
                    
                    Console.WriteLine($"[HISTORICAL WEATHER] Received {result?.Predictions?.Count ?? 0} weather predictions");
                    
                    if (result?.Predictions != null)
                    {
                        foreach (var prediction in result.Predictions)
                        {
                            Console.WriteLine($"[HISTORICAL WEATHER] {prediction.City}: {prediction.PredictedWeather} (confidence: {prediction.Confidence:F2})");
                        }
                    }
                    
                    return result?.Predictions ?? new List<WeatherPrediction>();
                }
                else
                {
                    Console.WriteLine($"[HISTORICAL WEATHER] Error: {response.StatusCode} - {response.ReasonPhrase}");
                    return await GetFallbackWeatherPredictions(cities, date);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[HISTORICAL WEATHER] Exception: {ex.Message}");
                return await GetFallbackWeatherPredictions(cities, date);
            }
        }

        //Hava durumu tahmini yapılamazsa varsayılan hava durumu tahmini
        private async Task<List<WeatherPrediction>> GetFallbackWeatherPredictions(List<string> cities, string date)
        {
            //Varsayılan hava durumu tahmin
            Console.WriteLine("[HISTORICAL WEATHER] Using fallback weather predictions");
            //Hava durumu tahmini 
            var predictions = new List<WeatherPrediction>();
            var month = ExtractMonthFromDate(date);
            //Şehir hava durumu tahmini
            foreach (var city in cities)
            {
                var weather = GetFallbackWeatherForCity(city, month);
                predictions.Add(new WeatherPrediction
                {
                    City = city,
                    Date = date,
                    Season = GetSeasonFromMonth(month),
                    PredictedWeather = weather,
                    Confidence = 0.6,
                    WeatherConditions = new List<string> { weather },
                    Explanation = $"{city} için varsayılan hava durumu: {weather}"
                });
            }
            
            return predictions;
        }
        //Tarih içinden ayı çekme kısmı
        private int ExtractMonthFromDate(string date)
        {
            try
            {
                //Ay isimleri ve ayların sayısal karşılığı
                var monthNames = new Dictionary<string, int>
                {
                    {"ocak", 1}, {"şubat", 2}, {"mart", 3}, {"nisan", 4}, {"mayıs", 5}, {"haziran", 6},
                    {"temmuz", 7}, {"ağustos", 8}, {"eylül", 9}, {"ekim", 10}, {"kasım", 11}, {"aralık", 12}
                };

                var parts = date.ToLower().Split(' ');
                foreach (var part in parts)
                {
                    if (monthNames.ContainsKey(part))
                    {
                        return monthNames[part];
                    }
                }
            }
            catch { }
            
            return DateTime.Now.Month; // Varsayılan olarak.
        }

        private string GetSeasonFromMonth(int month)
        {
            // Ayların hangi mevsimde olduğunu çekme
            return month switch
            {
                12 or 1 or 2 => "winter",
                3 or 4 or 5 => "spring",
                6 or 7 or 8 => "summer",
                _ => "autumn"
            };
        }

        //Şehir bazlı hava durumu tahmini
        private string GetFallbackWeatherForCity(string city, int month)
        {
            var cityLower = city.ToLower();
            var season = GetSeasonFromMonth(month);

            // Doğu Anadolu - Kış ağırlıklı
            if (cityLower.Contains("kars") || cityLower.Contains("erzurum") || cityLower.Contains("ağrı") || 
                cityLower.Contains("van") || cityLower.Contains("hakkari"))
            {
                return season == "winter" ? "kar" : "güneş";
            }
            
            // Karadeniz - Yağışlı
            if (cityLower.Contains("trabzon") || cityLower.Contains("rize") || cityLower.Contains("ordu") || 
                cityLower.Contains("sinop") || cityLower.Contains("artvin") || cityLower.Contains("giresun"))
            {
                return "yağmur";
            }
            
            // Akdeniz - Sıcak ve güneşli
            if (cityLower.Contains("antalya") || cityLower.Contains("mersin") || cityLower.Contains("adana") || 
                cityLower.Contains("hatay") || cityLower.Contains("muğla"))
            {
                return "güneş";
            }
            
            // Güneydoğu Anadolu - Sıcak ve kurak
            if (cityLower.Contains("diyarbakır") || cityLower.Contains("mardin") || cityLower.Contains("batman") || 
                cityLower.Contains("şanlıurfa") || cityLower.Contains("gaziantep"))
            {
                return season != "winter" ? "güneş" : "yağmur";
            }
            
            // Varsayılan
            return season == "summer" || season == "spring" ? "güneş" : "yağmur";
        }

        //ML servisinin sağlık kontrolü
        public async Task<bool> IsServiceHealthyAsync()
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

    //Hava durumu tahmini sınıfı
    public class WeatherPrediction
    {
        public string City { get; set; } = string.Empty;
        public string Date { get; set; } = string.Empty;
        public string Season { get; set; } = string.Empty;
        public string PredictedWeather { get; set; } = string.Empty;
        public double Confidence { get; set; }
        public List<string> WeatherConditions { get; set; } = new List<string>();
        public string Explanation { get; set; } = string.Empty;
    }

    //Hava durumu tahmini yanıt sınıfı
    public class WeatherPredictionResponse
    {
        public List<WeatherPrediction> Predictions { get; set; } = new List<WeatherPrediction>();
    }
} 