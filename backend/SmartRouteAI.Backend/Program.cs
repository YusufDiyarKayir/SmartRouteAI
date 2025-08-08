using DotNetEnv;
using SmartRouteAI.Backend.Models;

// Environment variables yükle
Env.Load();

var builder = WebApplication.CreateBuilder(args);

// Services
builder.Services.AddControllers();
builder.Services.AddHttpClient();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Dependency Injection
builder.Services.AddSingleton<SmartRouteAI.Backend.Services.PromptAnalysisService>();
builder.Services.AddSingleton<SmartRouteAI.Backend.Services.RouteOptimizationService>();
builder.Services.AddSingleton<SmartRouteAI.Backend.Services.MapService>();
builder.Services.AddSingleton<SmartRouteAI.Backend.Services.AdvancedWeatherService>();
builder.Services.AddSingleton<SmartRouteAI.Backend.Services.HolidayService>();
builder.Services.AddSingleton<SmartRouteAI.Backend.Services.AIModelService>();

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

// Middleware Pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.UseStaticFiles();
app.UseDefaultFiles();
app.MapControllers();
app.MapFallbackToFile("index.html");

app.Run();
