namespace SmartRouteAI.Backend.Models;

// API'ye gelen rota isteği modeli
public record RouteRequest(
    double FromLat,
    double FromLng,
    double ToLat,
    double ToLng,
    string Date,
    string Time
);
