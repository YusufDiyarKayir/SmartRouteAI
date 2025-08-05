using Azure.AI.TextAnalytics;
using Azure;
using System.Text.RegularExpressions;

namespace Services
{
    public class PromptAnalysisService
    {
        private readonly TextAnalyticsClient _client;
        private readonly List<string> _turkeyCities;
        private readonly List<string> _istanbulDistricts;
        // Köprü ve otoyol isimleri listesi
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
        // Otoyol tanımlamaları
        private static readonly List<(string Name, string Type, (double, double) Coord)> _highways = new()
        {
            ("Kuzey Marmara Otoyolu", "highway", (41.1815, 29.0736)),
            ("TEM Otoyolu", "highway", (41.0915, 29.0635)),
            ("O-7", "highway", (41.1815, 29.0736)),
            ("O-4", "highway", (41.0915, 29.0635)),
            ("E-5", "highway", (40.9903, 28.8034)), 
            ("D100", "highway", (41.1333, 29.0833)), 
        };

        //Prompt Analiz kısmı. Şehir isimleri ve İstanbul'un ilçelerini bu kısımda analiz ediyoruz.
        public PromptAnalysisService(IConfiguration config)
        {
            var endpoint = config["AzureCognitive:Endpoint"] ?? "";
            var apiKey = config["AzureCognitive:ApiKey"] ?? "";
            var credentials = new AzureKeyCredential(apiKey);
            _client = new TextAnalyticsClient(new Uri(endpoint), credentials);
            _turkeyCities = new List<string> {
                "Adana","Adıyaman","Afyonkarahisar","Ağrı","Amasya","Ankara","Antalya","Artvin","Aydın","Balıkesir","Bilecik","Bingöl","Bitlis","Bolu","Burdur","Bursa","Çanakkale","Çankırı","Çorum","Denizli","Diyarbakır","Edirne","Elazığ","Erzincan","Erzurum","Eskişehir","Gaziantep","Giresun","Gümüşhane","Hakkari","Hatay","Isparta","Mersin","İstanbul","İzmir","Kars","Kastamonu","Kayseri","Kırklareli","Kırşehir","Kocaeli","Konya","Kütahya","Malatya","Manisa","Kahramanmaraş","Mardin","Muğla","Muş","Nevşehir","Niğde","Ordu","Rize","Sakarya","Samsun","Siirt","Sinop","Sivas","Tekirdağ","Tokat","Trabzon","Tunceli","Şanlıurfa","Uşak","Van","Yozgat","Zonguldak","Aksaray","Bayburt","Karaman","Kırıkkale","Batman","Şırnak","Bartın","Ardahan","Iğdır","Yalova","Karabük","Kilis","Osmaniye","Düzce"
            };
            
            // İstanbul ilçeleri listesi
            _istanbulDistricts = new List<string> {
                "Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy", "Esenler", "Esenyurt", "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Halkalı", "Kadıköy", "Kağıthane", "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer", "Silivri", "Sultanbeyli", "Sultangazi", "Şile", "Şişli", "Tuzla", "Ümraniye", "Üsküdar", "Zeytinburnu"
            };
        }

        // Ay isimleri ve ayların sayısal karşılığı
        private string GetMonthNumber(string monthName)
        {
            var months = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                {"Ocak", "01"}, {"Şubat", "02"}, {"Mart", "03"}, {"Nisan", "04"},
                {"Mayıs", "05"}, {"Haziran", "06"}, {"Temmuz", "07"}, {"Ağustos", "08"},
                {"Eylül", "09"}, {"Ekim", "10"}, {"Kasım", "11"}, {"Aralık", "12"}
            };
            return months.TryGetValue(monthName, out var number) ? number : "01";
        }

        // Anlamsız prompt'ları tespit eden validasyon metodu
        private bool IsMeaninglessPrompt(string prompt)
        {
            if (string.IsNullOrWhiteSpace(prompt))
                return true;

            var promptLower = prompt.ToLower().Trim();
            
            // Çok kısa prompt'lar (2 karakterden az)
            if (promptLower.Length < 2)
                return true;

            // Sadece sayılar, semboller veya tekrarlayan karakterler
            if (Regex.IsMatch(promptLower, @"^[\d\s\W]+$"))
                return true;

            // Sadece tekrarlayan karakterler (aaa, bbb, 111 gibi)
            if (Regex.IsMatch(promptLower, @"^(.)\1+$"))
                return true;

            // Anlamsız kelime kombinasyonları - daha katı kontrol
            var meaninglessPatterns = new[]
            {
                @"^(test|deneme|asdf|qwerty|xyz|abc|123|456|789)$", // Test kelimeleri
                @"^(merhaba|selam|hi|hello|bye|görüşürüz)$", // Sadece selamlaşma
                @"^(nasılsın|iyi|kötü|güzel)$", // Sadece durum belirten kelimeler
            };

            foreach (var pattern in meaninglessPatterns)
            {
                if (Regex.IsMatch(promptLower, pattern))
                    return true;
            }

            // En az bir Türkiye şehri veya İstanbul ilçesi içermeli
            bool hasValidLocation = false;
            
            // İstanbul ilçelerini kontrol et
            foreach (var district in _istanbulDistricts)
            {
                if (promptLower.Contains(district.ToLower()))
                {
                    hasValidLocation = true;
                    break;
                }
            }
            
            // Türkiye şehirlerini kontrol et
            if (!hasValidLocation)
            {
                foreach (var city in _turkeyCities)
                {
                    if (promptLower.Contains(city.ToLower()))
                    {
                        hasValidLocation = true;
                        break;
                    }
                }
            }

            // Rota ile ilgili anahtar kelimeler var mı kontrol et
            var routeKeywords = new[]
            {
                "git", "gideyim", "gidelim", "gidiyorum", "gidiyoruz",
                "rota", "yol", "güzergah", "harita", "navigasyon",
                "nereden", "nereye", "başlangıç", "varış", "hedef",
                "ulaşım", "seyahat", "yolculuk", "gezi", "tur",
                "otobüs", "tren", "uçak", "araba", "araç", "vasıta",
                "köprü", "otoyol", "karayolu", "yol", "cadde", "sokak"
            };

            bool hasRouteKeyword = routeKeywords.Any(keyword => promptLower.Contains(keyword));

            // Eğer geçerli bir lokasyon yoksa ve rota ile ilgili anahtar kelime de yoksa anlamsız kabul et
            if (!hasValidLocation && !hasRouteKeyword)
                return true;

            return false;
        }

        public async Task<PromptAnalysisResult> AnalyzePromptAsync(string prompt)
        {
            // Anlamsız prompt kontrolü
            if (IsMeaninglessPrompt(prompt))
            {
                Console.WriteLine($"[PROMPT] Anlamsız prompt tespit edildi: '{prompt}'");
                throw new InvalidOperationException("Sizi anlayamadım, lütfen tekrar bir rota oluşturunuz.");
            }

            // 1. Azure ile varlık ve anahtar kelime çıkarımı
            var entities = await _client.RecognizeEntitiesAsync(prompt);
            var keyPhrases = await _client.ExtractKeyPhrasesAsync(prompt);
            
            // Azure servislerinden gelen yanıtları kontrol et
            if (entities?.Value == null || keyPhrases?.Value == null)
            {
                Console.WriteLine("[PROMPT] Warning: Azure services returned null response");
                return new PromptAnalysisResult();
            }
            
            // Prompt'u küçük harfe çevir (hava koşulları analizi için)
            var promptLower = prompt.ToLower();

            // 2. Türkiye şehirlerini ve İstanbul ilçelerini prompt içinde bul
            var foundCities = new List<string>();
            var promptWords = Regex.Split(prompt, @"[\s,.;:!?()\[\]\-/]+")
                .Where(w => !string.IsNullOrWhiteSpace(w)).ToList();
            
            // Önce İstanbul ilçelerini kontrol et
            foreach (var district in _istanbulDistricts)
            {
                if (prompt.IndexOf(district, StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    var combined = $"{district}, İstanbul";
                    if (!foundCities.Contains(combined, StringComparer.OrdinalIgnoreCase))
                        foundCities.Add(combined);
                }
            }
            
            // Sonra şehirleri kontrol et
            var cityPattern = string.Join("|", _turkeyCities.Select(Regex.Escape));
            var regex = new Regex($@"((\w+)[/\\-])?({cityPattern})", RegexOptions.IgnoreCase);
            foreach (Match match in regex.Matches(prompt))
            {
                if (match.Success)
                {
                    var city = match.Groups[3].Value;
                    var district = match.Groups[2].Success ? match.Groups[2].Value : null;
                    if (!string.IsNullOrEmpty(district))
                    {
                        var combined = $"{district}, {city}";
                        if (!foundCities.Contains(combined, StringComparer.OrdinalIgnoreCase))
                            foundCities.Add(combined);
                    }
                    if (!foundCities.Contains(city, StringComparer.OrdinalIgnoreCase))
                        foundCities.Add(city);
                }
            }
            // Eğer yukarıdaki regex ile hiç şehir bulunamazsa, eski kelime kökü mantığıyla bul
            if (foundCities.Count == 0)
            {
                foreach (var word in promptWords)
                {
                    // '/' veya ',' ile ayrılmışsa son parçayı şehir olarak dene
                    var parts = word.Split(new[] {'/', ','}, StringSplitOptions.RemoveEmptyEntries);
                    var lastPart = parts.Length > 1 ? parts[parts.Length-1].Trim() : word.Trim();
                    
                    // Önce İstanbul ilçelerini kontrol et
                    foreach (var district in _istanbulDistricts)
                    {
                        if (string.Equals(district, lastPart, StringComparison.OrdinalIgnoreCase))
                        {
                            var combined = $"{district}, İstanbul";
                            if (!foundCities.Contains(combined, StringComparer.OrdinalIgnoreCase))
                                foundCities.Add(combined);
                        }
                    }
                    
                    // Sonra şehirleri kontrol et
                    foreach (var city in _turkeyCities)
                    {
                        if (string.Equals(city, lastPart, StringComparison.OrdinalIgnoreCase))
                        {
                            if (!foundCities.Contains(city, StringComparer.OrdinalIgnoreCase))
                                foundCities.Add(city);
                        }
                    }
                }
            }

            // Eğer hala hiç şehir bulunamadıysa, anlamsız prompt olarak kabul et
            if (foundCities.Count == 0)
            {
                Console.WriteLine($"[PROMPT] Hiç şehir bulunamadı: '{prompt}'");
                throw new InvalidOperationException("Sizi anlayamadım, lütfen tekrar bir rota oluşturunuz.");
            }

            // 3. Azure'dan dönen entity'ler arasında şehir/yer olanları ekle
            var azureCities = entities.Value
                .Where(e => e.Category == "Location" || e.Category == "Address" || e.Category == "Organization")
                .Select(e => e.Text)
                .Distinct()
                .ToList();
            
            // Önce İstanbul ilçelerini kontrol et
            foreach (var city in azureCities)
            {
                if (_istanbulDistricts.Any(c => c.Equals(city, StringComparison.OrdinalIgnoreCase)) &&
                    !foundCities.Contains($"{city}, İstanbul", StringComparer.OrdinalIgnoreCase))
                {
                    foundCities.Add($"{city}, İstanbul");
                }
            }
            
            // Sonra şehirleri kontrol et
            foreach (var city in azureCities)
            {
                if (_turkeyCities.Any(c => c.Equals(city, StringComparison.OrdinalIgnoreCase)) &&
                    !foundCities.Contains(city, StringComparer.OrdinalIgnoreCase))
                {
                    foundCities.Add(city);
                }
            }

            // 4. Anahtar istekler (Azure'dan gelen key phrase'ler)
            var requests = keyPhrases.Value.ToList();
            
            // Hava koşullarının promptan analizi
            var weatherConditions = new List<string>();
            
            // Hava durumu kelimeleri ve eşleştirme kuralları
            var weatherPatterns = new Dictionary<string, string>
            {
                { @"\byağmurlu\b", "yağmurlu" },
                { @"\bkarlı\b", "karlı" },
                { @"\bgüneşli\b", "güneşli" },
                { @"\bsisli\b", "sisli" },
                { @"\brüzgarlı\b", "rüzgarlı" },
                { @"\bfırtınalı\b", "fırtınalı" },
                { @"\byağmur\b", "yağmur" },
                { @"\bkar\b", "kar" },
                { @"\bgüneş\b", "güneş" },
                { @"\bsis\b", "sis" },
                { @"\brüzgar\b", "rüzgar" },
                { @"\bfırtına\b", "fırtına" }
            };
            
            foreach (var pattern in weatherPatterns)
            {
                if (Regex.IsMatch(promptLower, pattern.Key))
                {
                    weatherConditions.Add(pattern.Value);
                }
            }
            
            // Tarih analizi
            string? travelDate = null;
            
            // DD.MM.YYYY formatı (12.02.2026)
            var dotDatePattern = @"(\d{1,2})\.(\d{1,2})\.(\d{4})";
            var dotDateMatch = Regex.Match(prompt, dotDatePattern);
            if (dotDateMatch.Success)
            {
                var day = dotDateMatch.Groups[1].Value;
                var month = dotDateMatch.Groups[2].Value;
                var year = dotDateMatch.Groups[3].Value;
                travelDate = $"{year}-{month.PadLeft(2, '0')}-{day.PadLeft(2, '0')}";
            }
            else
            {
                // Gün ay formatı (2025 yılı olarak algıla)
                var dayMonthPattern = @"(\d{1,2})\s*(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)";
                var dayMonthMatch = Regex.Match(prompt, dayMonthPattern, RegexOptions.IgnoreCase);
                if (dayMonthMatch.Success)
                {
                    var day = dayMonthMatch.Groups[1].Value;
                    var month = dayMonthMatch.Groups[2].Value;
                    var year = 2025; // 2025 yılı olarak sabit
                    travelDate = $"{year}-{GetMonthNumber(month)}-{day.PadLeft(2, '0')}";
                }
                else
                {
                    // Gün ay yıl formatı
                    var fullDatePattern = @"(\d{1,2})\s*(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s*(\d{4})";
                    var fullDateMatch = Regex.Match(prompt, fullDatePattern, RegexOptions.IgnoreCase);
                    if (fullDateMatch.Success)
                    {
                        var day = fullDateMatch.Groups[1].Value;
                        var month = fullDateMatch.Groups[2].Value;
                        var year = fullDateMatch.Groups[3].Value;
                        travelDate = $"{year}-{GetMonthNumber(month)}-{day.PadLeft(2, '0')}";
                    }
                    else
                    {
                        // Sadece ay isimleri (2025 yılı olarak algıla)
                        var monthPattern = @"(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)";
                        var monthMatch = Regex.Match(prompt, monthPattern, RegexOptions.IgnoreCase);
                        if (monthMatch.Success)
                        {
                            var month = monthMatch.Groups[1].Value;
                            var year = 2025; // 2025 yılı olarak sabit
                            travelDate = $"{year}-{GetMonthNumber(month)}-01";
                        }
                    }
                }
            }
            
            // Saat analizi 
            var timePattern = @"(\d{1,2}):(\d{2})";
            var timeMatch = Regex.Match(prompt, timePattern);
            string? travelTime = null;
            if (timeMatch.Success)
            {
                var hour = timeMatch.Groups[1].Value;
                var minute = timeMatch.Groups[2].Value;
                travelTime = $"{hour.PadLeft(2, '0')}:{minute}";
            }
            
            // Havayı ve tarihi request olarak döndürmek
            if (weatherConditions.Any())
            {
                requests.Add($"Hava koşulları: {string.Join(", ", weatherConditions)}");
            }
            if (!string.IsNullOrEmpty(travelDate))
            {
                requests.Add($"Seyahat tarihi: {travelDate}");
            }
            if (!string.IsNullOrEmpty(travelTime))
            {
                requests.Add($"Seyahat saati: {travelTime}");
            }

            // Şehirleri prompt'taki waypoints ve diğer bağlamları göze alarak sıraya göre düzenle
            var orderedCities = new List<string>();
            
            // Prompt'taki şehir sırasını analiz et
            var cityPositions = new List<(string city, int position)>();
            
            foreach (var city in foundCities)
            {
                var cityName = city.Split(',')[0].Trim().ToLower();
                var position = promptLower.IndexOf(cityName);
                if (position >= 0)
                {
                    cityPositions.Add((city, position));
                }
            }
            
            // Şehirleri Pozisyona göre sırala
            orderedCities = cityPositions.OrderBy(x => x.position).Select(x => x.city).ToList();
            
            // Eğer sıralama başarısız olursa, orijinal listeyi kullan
            if (orderedCities.Count == 0)
            {
                orderedCities = foundCities;
            }
            
            string source = orderedCities.Count > 0 ? orderedCities[0] : "";
            string destination = orderedCities.Count > 1 ? orderedCities[^1] : "";
            var waypoints = orderedCities.Skip(1).Take(orderedCities.Count - 2).ToList();

            //  Sıralı şehirler
            var route = orderedCities;
            
            // ML servisi hava durumu tahmini - AdvancedWeatherService kullanılacak
            var mlWeatherConditions = new List<string>();

            // Debug bilgileri
            Console.WriteLine($"[PROMPT] Original prompt: '{prompt}'");
            Console.WriteLine($"[PROMPT] Found cities: {string.Join(", ", foundCities)}");
            Console.WriteLine($"[PROMPT] Ordered cities: {string.Join(", ", orderedCities)}");
            Console.WriteLine($"[PROMPT] Source: {source}");
            Console.WriteLine($"[PROMPT] Destination: {destination}");
            Console.WriteLine($"[PROMPT] Waypoints: {string.Join(", ", waypoints)}");
            Console.WriteLine($"[PROMPT] Travel Date: '{travelDate}'");
            Console.WriteLine($"[PROMPT] Travel Time: '{travelTime}'");
            Console.WriteLine($"[PROMPT] ML Weather Conditions: {string.Join(", ", mlWeatherConditions)}");


            // Köprü ve otoyol şartlarını tespit et
            var bridgeDirectives = new List<(string Name, bool Use)>();
            foreach (var (name, type, coord) in _bridges)
            {
                if (prompt.IndexOf(name, StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    // Kullan/kullanma/geç/geçme Şart kontrolü
                    bool use = true;
                    if (Regex.IsMatch(prompt, $@"{name}.*(geçme|kullanma)", RegexOptions.IgnoreCase) ||
                        Regex.IsMatch(prompt, $@"(geçmeden|kullanmadan).*{name}", RegexOptions.IgnoreCase))
                        use = false;
                    else if (Regex.IsMatch(prompt, $@"{name}.*(geç|kullan)", RegexOptions.IgnoreCase) ||
                             Regex.IsMatch(prompt, $@"(geçerek|kullanarak).*{name}", RegexOptions.IgnoreCase))
                        use = true;
                    bridgeDirectives.Add((name, use));
                }
            }
            var highwayDirectives = new List<(string Name, bool Use)>();
            foreach (var (name, type, coord) in _highways)
            {
                if (prompt.IndexOf(name, StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    bool use = true;
                    if (Regex.IsMatch(prompt, $@"{name}.*(kullanma|geçme)", RegexOptions.IgnoreCase) ||
                        Regex.IsMatch(prompt, $@"(kullanmadan|geçmeden).*{name}", RegexOptions.IgnoreCase))
                        use = false;
                    else if (Regex.IsMatch(prompt, $@"{name}.*(kullan|geç)", RegexOptions.IgnoreCase) ||
                             Regex.IsMatch(prompt, $@"(kullanarak|geçerek).*{name}", RegexOptions.IgnoreCase))
                        use = true;
                    highwayDirectives.Add((name, use));
                }
            }

            return new PromptAnalysisResult
            {
                Source = source,
                Destination = destination,
                Requests = requests,
                Route = route,
                BridgeDirectives = bridgeDirectives,
                HighwayDirectives = highwayDirectives,
                WeatherConditions = weatherConditions,
                TravelDate = travelDate,
                TravelTime = travelTime
            };
        }
    }

    public class PromptAnalysisResult
    {
        public string Source { get; set; } = string.Empty;
        public string Destination { get; set; } = string.Empty;
        public List<string> Requests { get; set; } = new List<string>();
        public List<string> Route { get; set; } = new List<string>();
        public List<(string Name, bool Use)> BridgeDirectives { get; set; } = new();
        public List<(string Name, bool Use)> HighwayDirectives { get; set; } = new();
        public List<string> WeatherConditions { get; set; } = new List<string>();
        public string? TravelDate { get; set; }
        public string? TravelTime { get; set; }
    }
} 