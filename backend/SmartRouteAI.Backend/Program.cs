using System.Net.Http; // HTTP istekleri için gerekli kütüphane
using System.Net.Http.Json; // JSON verileriyle HTTP işlemleri için kolaylık sağlar
using Azure.AI.TextAnalytics;
using Google.OrTools.ConstraintSolver;

var builder = WebApplication.CreateBuilder(args); // Web uygulaması için yapılandırıcı oluştur

builder.Services.AddControllers();
builder.Services.AddHttpClient();
builder.Services.AddSingleton<Services.PromptAnalysisService>();
builder.Services.AddSingleton<Services.RouteOptimizationService>();
builder.Services.AddSingleton<Services.MapService>();
builder.Services.AddSingleton<Services.AdvancedWeatherService>();
builder.Services.AddSingleton<Services.HolidayService>();
builder.Services.AddSingleton<Services.AIModelService>();

builder.Services.AddAuthorization();

// CORS (Cross-Origin Resource Sharing) ayarları ekleniyor
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()   // Tüm kaynaklara izin ver
              .AllowAnyHeader()   // Tüm başlıklara izin ver
              .AllowAnyMethod();  // GET, POST, PUT vb. tüm HTTP metodlarına izin ver
    });
});

// Swagger ve Endpoint desteği ekleniyor (dökümantasyon için)
builder.Services.AddEndpointsApiExplorer(); 
builder.Services.AddSwaggerGen(); 

var app = builder.Build(); // Uygulama nesnesi oluşturuluyor

// Geliştirme ortamındaysa Swagger arayüzünü aktif et
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// CORS politikası uygulamaya dahil ediliyor
app.UseCors();
app.UseAuthorization();
app.MapControllers();

// Frontend dosyalarını serve et
app.UseStaticFiles();
app.UseDefaultFiles();

// Frontend için fallback route
app.MapFallbackToFile("index.html");

// Hava durumu özetleri için örnek string dizisi
var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", 
    "Balmy", "Hot", "Sweltering", "Scorching"
};

// Basit bir GET endpoint: /weatherforecast
app.MapGet("/weatherforecast", () =>
{
    // 5 günlük hava durumu simülasyonu üretiliyor
    var forecast =  Enumerable.Range(1, 5).Select(index =>
        new WeatherForecast
        (
            DateOnly.FromDateTime(DateTime.Now.AddDays(index)), // ileri tarihler
            Random.Shared.Next(-20, 55), // rastgele sıcaklık
            summaries[Random.Shared.Next(summaries.Length)] // rastgele özet
        ))
        .ToArray();
    return forecast;
})
.WithName("GetWeatherForecast") // Swagger adı
.WithOpenApi(); // OpenAPI desteği

// Kullanıcıdan gelen başlangıç ve varış bilgileriyle rota hesaplama
app.MapPost("/route", async (RouteRequest request) =>
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
    bool isHoliday = false;
    try {
        using var http = new HttpClient();
        string holidayApiKey = "e07f6c1c-7dad-4745-8779-d91c690c059c";
        string holidayUrl = $"https://holidays.abstractapi.com/v1/?api_key={holidayApiKey}&country=TR&year={dt.Year}&month={dt.Month}&day={dt.Day}";
        var holidayResp = await http.GetStringAsync(holidayUrl);
        isHoliday = !string.IsNullOrWhiteSpace(holidayResp) && holidayResp != "[]";
    } catch { }

    // 2. Hava durumu bilgisi: OpenWeatherMap API üzerinden
    string weather = "Sunny";
    string weatherDesc = "";
    try {
        using var http = new HttpClient();
        string weatherApiKey = "0d97a7dabc935b1c450dbe82a3234617";
        string forecastUrl = $"https://api.openweathermap.org/data/2.5/forecast?lat={fromLat}&lon={fromLng}&appid={weatherApiKey}&lang=tr&units=metric";
        var forecastResp = await http.GetFromJsonAsync<OpenWeatherForecastResponse>(forecastUrl);
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
    string googleApiKey = "AIzaSyCTl8gXrbbcPDOolXt8OpuzQghwXQl_N9Y";
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
            int minDurationIdx = 0;
            int minTollIdx = 0;
            int minDuration = int.MaxValue;
            int minToll = int.MaxValue;

            // Güzergahları kontrol et
            for (int i = 0; i < googleObj.routes.Length; i++)
            {
                var r = googleObj.routes[i];
                var leg = r.legs[0];
                double durationMin = leg.duration_in_traffic != null ? leg.duration_in_traffic.value / 60.0 : leg.duration.value / 60.0;
                int tollCount = 0;

                if (leg.steps != null)
                {
                    foreach (var step in leg.steps)
                    {
                        if (step.html_instructions != null && (step.html_instructions.ToLower().Contains("toll") || step.html_instructions.ToLower().Contains("ücretli")))
                            tollCount++;
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
                        if (step.html_instructions != null && (step.html_instructions.ToLower().Contains("toll") || step.html_instructions.ToLower().Contains("ücretli")))
                            tollCount++;
                    }
                }

                string tollClass = "Yok";
                if (tollCount == 1 || tollCount == 2) tollClass = "Orta";
                else if (tollCount >= 3) tollClass = "Yüksek";
                string tollInfo = $"Tahmini {tollCount} adet ücretli geçiş olabilir.";

                string title = $"Alternatif {i+1}";
                if (i == minDurationIdx) title += " - En hızlı";
                if (i == minTollIdx) title += " - En düşük maliyetli";
                if (tollCount == 0) title += " - Ücretsiz";

                var arrival = dt.AddMinutes(durationMin);
                string arrivalStr = arrival.ToString("dd MMMM yyyy HH:mm", new System.Globalization.CultureInfo("tr-TR"));

                routes.Add(new {
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
        }
    }
    catch (Exception ex)
    {
        // Hata olursa varsayılan rota döndür
        routes.Clear();
        routes.Add(new { title = "Hata", distanceKm = 0, estimatedDurationMinutes = 0, polyline = "", tollClass = "-", error = ex.Message });
    }

    // Sonuçlar JSON olarak döndürülüyor
    return Results.Ok(new
    {
        routes,
        date,
        time,
        isHoliday,
        weather,
        trafficLevel
    });
})
.WithName("GetRouteEstimate")
.WithOpenApi(); // Swagger/OpenAPI için

app.Run(); // Uygulamayı çalıştır

// Hava durumu kaydı
record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556); // Fahrenheit dönüşüm
}

// API'ye gelen rota isteği modeli
record RouteRequest(
    double FromLat,
    double FromLng,
    double ToLat,
    double ToLng,
    string Date,
    string Time
);

// Google Directions API yanıt modeli
public class GoogleDirectionsResponse {
    public GoogleRoute[] routes { get; set; }
}
public class GoogleRoute {
    public GoogleLeg[] legs { get; set; }
    public GooglePolyline overview_polyline { get; set; }
}
public class GoogleLeg {
    public GoogleValue distance { get; set; }
    public GoogleValue duration { get; set; } = new GoogleValue();
    public GoogleValue duration_in_traffic { get; set; } = new GoogleValue();
    public GoogleStep[] steps { get; set; }
}
public class GoogleStep {
    public string html_instructions { get; set; }
}
public class GoogleValue {
    public double value { get; set; }
    public string text { get; set; }
}
public class GooglePolyline {
    public string points { get; set; }
}

// OpenWeatherMap API yanıt modelleri
public class OpenWeatherResponse {
    public WeatherDesc[] weather { get; set; }
}
public class WeatherDesc {
    public string main { get; set; }
    public string description { get; set; }
}

// OpenWeatherMap forecast yanıt modeli
public class OpenWeatherForecastResponse {
    public ForecastItem[] list { get; set; }
}
public class ForecastItem {
    public long dt { get; set; }
    public WeatherDesc[] weather { get; set; }
}
