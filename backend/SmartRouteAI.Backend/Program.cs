using DotNetEnv;

// .env dosyasını yükle
Env.Load();

var builder = WebApplication.CreateBuilder(args);

// Services
builder.Services.AddControllers();
builder.Services.AddHttpClient();
builder.Services.AddSingleton<Services.PromptAnalysisService>();
builder.Services.AddSingleton<Services.RouteOptimizationService>();
builder.Services.AddSingleton<Services.MapService>();
builder.Services.AddSingleton<Services.AdvancedWeatherService>();
builder.Services.AddSingleton<Services.HolidayService>();
builder.Services.AddSingleton<Services.AIModelService>();

builder.Services.AddAuthorization();

// CORS ayarları
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Middleware pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.UseAuthorization();
app.MapControllers();

// Static files
app.UseStaticFiles();
app.UseDefaultFiles();
app.MapFallbackToFile("index.html");

app.Run();
