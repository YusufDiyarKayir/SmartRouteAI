# Backend (ASP.NET Core Web API)

This folder contains the ASP.NET Core Web API project for SmartRouteAI.

## Project Structure

```
backend/SmartRouteAI.Backend/
├── Controllers/
│   └── RouteController.cs          # API endpoints
├── Services/
│   ├── PromptAnalysisService.cs    # NLP operations
│   ├── RouteOptimizationService.cs # Route optimization
│   ├── MapService.cs              # Map operations
│   ├── AdvancedWeatherService.cs  # Weather analysis
│   ├── HolidayService.cs          # Holiday checking
│   └── AIModelService.cs          # AI model integration
├── wwwroot/
│   └── index.html                 # Frontend file
├── appsettings.json               # Configuration
├── Program.cs                     # Application configuration
└── SmartRouteAI.Backend.csproj    # Project file
```

## Setup

To set up the backend project, run the following command in the main directory:

```bash
dotnet new webapi
```

## Running the Backend

### Development Mode
```bash
cd backend/SmartRouteAI.Backend
dotnet run
```

### Production Mode
```bash
cd backend/SmartRouteAI.Backend
dotnet build
dotnet run --environment Production
```

## Configuration

The backend uses `appsettings.json` for configuration. Key settings include:

- API Keys for external services
- Database connection strings
- Logging configuration
- CORS settings

## API Endpoints

### Main Endpoints
- `POST /api/Route/analyze-prompt` - Prompt analysis
- `POST /api/Route/plan` - Route planning
- `GET /api/Route/health` - Service status

### Weather
- `GET /weatherforecast` - Weather forecast

### Route Calculation
- `POST /route` - Coordinate-based route calculation

## Dependencies

The backend requires the following NuGet packages:
- Microsoft.AspNetCore.App
- System.Net.Http
- Newtonsoft.Json
- Azure.AI.TextAnalytics (for NLP features)

## Port Configuration

By default, the backend runs on:
- Development: http://localhost:5077
- Production: Configured via environment variables

## Health Checks

The backend includes health check endpoints to monitor service status and dependencies. 