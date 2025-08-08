namespace SmartRouteAI.Backend.Services
{
    public class MapService
    {
        private readonly string _apiKey;
        public MapService(IConfiguration config)
        {
            _apiKey = Environment.GetEnvironmentVariable("GOOGLE_MAPS_API_KEY") ?? "";
        }

        // Şimdilik mock bir harita url'si dönüyoruz
        public Task<string> GetMapUrlAsync(List<string> route)
        {
            // Gerçek Google Maps entegrasyonu burada olacak
            var url = "https://maps.google.com/?q=" + string.Join("|", route);
            return Task.FromResult(url);
        }
    }
} 