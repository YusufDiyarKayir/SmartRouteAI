namespace SmartRouteAI.Backend.Models;

// Hava durumu kaydı
public record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556); // Fahrenheit dönüşüm
}
