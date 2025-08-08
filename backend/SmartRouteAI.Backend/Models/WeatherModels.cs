namespace SmartRouteAI.Backend.Models;

// OpenWeatherMap API yanıt modelleri
public class OpenWeatherResponse 
{
    public WeatherDesc[] weather { get; set; } = Array.Empty<WeatherDesc>();
}

public class WeatherDesc 
{ 
    public string main { get; set; } = string.Empty;
    public string description { get; set; } = string.Empty;
}

// OpenWeatherMap forecast yanıt modeli
public class OpenWeatherForecastResponse 
{
    public ForecastItem[] list { get; set; } = Array.Empty<ForecastItem>();
}

public class ForecastItem 
{
    public long dt { get; set; }
    public WeatherDesc[] weather { get; set; } = Array.Empty<WeatherDesc>();
}
