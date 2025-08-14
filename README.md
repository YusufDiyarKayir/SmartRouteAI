# SmartRouteAI - Intelligent Route Planning System

## Project Overview

SmartRouteAI is an AI-powered advanced route planning system that provides intelligent route optimization using natural language processing, machine learning weather prediction, and real-time traffic analysis.

## Features

### AI-Powered Features
- **Natural Language Processing (NLP)**: Users can request routes using natural sentences like "Go from Istanbul to Ankara"
- **Smart Prompt Analysis**: Advanced text analysis with Azure Text Analytics
- **Invalid Prompt Detection**: Automatically detects invalid requests
- **ML-Based Weather Analysis**: Weather prediction using LSTM + Transformer models
- **Route Optimization**: AI-powered route optimization algorithms
- **Traffic Prediction**: Machine learning-based traffic pattern analysis

### Map and Route Features
- **Google Maps Integration**: Real-time map viewing and route visualization
- **Alternative Routes**: Multiple route options with optimization
- **Real-Time Traffic**: Route updates based on traffic conditions
- **Toll Road Detection**: Calculation of highway and bridge tolls
- **Arrival Time Calculation**: Arrival estimation based on traffic and weather

### Weather Integration
- **OpenWeatherMap API**: Real-time weather data integration
- **Weather Impact Analysis**: Effect of rain, snow, fog on route duration
- **Advanced Weather Prediction**: ML-based weather forecasting
- **Weather Classification**: Automatic weather categorization
- **Historical Weather Data**: Analysis of past weather patterns

### Holiday and Time Management
- **Abstract API Integration**: Turkey holiday day checking
- **Holiday Impact Calculation**: Traffic density analysis on holidays
- **Weekend Optimization**: Route adjustment based on weekend traffic
- **Time-Based Routing**: Optimized routes for specific times and dates

### User Experience
- **Modern Web Interface**: Responsive and user-friendly design
- **Real-Time Updates**: Instant route and weather updates
- **Error Handling**: Comprehensive error catching and user notification
- **Multi-Language Support**: Turkish interface and messages

## Technical Architecture

### Backend (ASP.NET Core 8.0)
```
backend/SmartRouteAI.Backend/
├── Controllers/
│   ├── RouteController.cs          # Route planning API endpoints
│   └── WeatherController.cs        # Weather data API endpoints
├── Services/
│   ├── PromptAnalysisService.cs    # NLP operations
│   ├── RouteOptimizationService.cs # Route optimization
│   ├── MapService.cs              # Map operations
│   ├── AdvancedWeatherService.cs  # Weather analysis
│   ├── HolidayService.cs          # Holiday checking
│   └── AIModelService.cs          # AI model integration
├── Models/
│   ├── GoogleDirectionsModels.cs  # Google Maps response models
│   ├── PromptRequest.cs           # NLP request models
│   ├── RouteRequest.cs            # Route request models
│   ├── WeatherForecast.cs         # Weather forecast models
│   └── WeatherModels.cs           # Weather data models
├── wwwroot/
│   ├── index.html                 # Frontend interface
│   └── styles.css                 # Frontend styling
└── Program.cs                     # Application configuration
```

### Python ML Services
```
ml_service/
├── ai_service.py                  # Main AI service integration
├── advanced_weather_api.py        # Advanced weather API
├── advanced_weather_data.py       # Weather data processing
├── advanced_weather_predictor.py  # Weather prediction models
├── historical_weather_data.py     # Historical weather analysis
├── historical_weather_predictor.py # Historical prediction models
├── route_optimization_ai.py       # Route optimization AI
├── traffic_ai_model.py            # Traffic prediction models
├── train_ai_models.py             # AI model training
├── test_api.py                    # API testing utilities
└── requirements.txt               # Python dependencies
```

### Models and Data
```
models/
├── traffic_prediction_metadata.json # Traffic model metadata
└── training_results.json          # Training performance data
```

### Testing
```
tests/
├── test_system.py                 # System integration tests
└── README.md                      # Testing documentation
```

## Installation and Setup

### Requirements
- .NET 8.0 SDK
- Python 3.8+
- Git
- PowerShell (for Windows)

### API Key Setup

1. **OpenWeatherMap API Key (Required):**
   - Go to [OpenWeatherMap](https://openweathermap.org/api)
   - Create a free account
   - Get your API key
   - Used for real-time weather data and forecasts

2. **Google Maps API Key (Required):**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Maps JavaScript API and Directions API
   - Get your API key
   - Used for route calculation and map integration

3. **Abstract API Holiday Key (Optional):**
   - Go to [Abstract API](https://www.abstractapi.com/holidays-api)
   - Create a free account
   - Get your API key
   - Used for Turkey holiday day checking

4. **Azure Cognitive Services API Key (Optional):**
   - Go to [Azure Portal](https://portal.azure.com/)
   - Create a Cognitive Services resource
   - Get your API key
   - Used for advanced text analysis and NLP features

### Installation Steps

1. **Clone the project:**
```bash
git clone https://github.com/YusufDiyarKayir/SmartRouteAI.git
cd SmartRouteAI
```

2. **Configure API keys in appsettings.json:**
```json
{
  "OpenWeatherMap": {
    "ApiKey": "your_openweather_api_key_here"
  },
  "GoogleMaps": {
    "ApiKey": "your_google_maps_api_key_here"
  },
  "AbstractAPI": {
    "ApiKey": "your_abstract_api_key_here"
  },
  "AzureCognitive": {
    "ApiKey": "your_azure_cognitive_api_key_here"
  }
}
```

3. **Install Python dependencies:**
```bash
cd ml_service
pip install -r requirements.txt
cd ..
```

4. **Start the project:**
```bash
.\projeyi_baslat.ps1
```

5. **Access the application:**
```
http://localhost:5077
```

## API Endpoints

### Route Planning
- `POST /api/Route/analyze-prompt` - Natural language prompt analysis
- `POST /api/Route/plan` - AI-powered route planning
- `GET /api/Route/health` - Service health check

### Weather Services
- `GET /api/Weather/forecast` - Weather forecast data
- `GET /api/Weather/current` - Current weather conditions
- `GET /api/Weather/historical` - Historical weather analysis

### AI Services
- `POST /api/AI/optimize-route` - AI route optimization
- `POST /api/AI/predict-traffic` - Traffic prediction
- `POST /api/AI/analyze-weather` - Weather impact analysis

## Configuration

### Required API Keys
The following API keys are required for full functionality:

- **OpenWeatherMap API Key**: For weather data and forecasts
- **Google Maps API Key**: For route calculation and map integration
- **Abstract API Key**: For holiday checking (optional)
- **Azure Cognitive Services Key**: For advanced NLP (optional)

### Environment Configuration
The application uses `appsettings.json` for configuration. Ensure all API keys are properly configured before running the application.

## Performance Features

- **Fast Response**: Average 2-3 seconds route calculation time
- **High Accuracy**: 95%+ weather prediction accuracy using ML models
- **Scalable Architecture**: Microservice-based design for easy scaling
- **Cache System**: 5-minute cache for improved performance
- **Real-Time Updates**: Live traffic and weather data integration

## Testing

### Backend Testing
```bash
cd backend/SmartRouteAI.Backend
dotnet test
```

### Python Services Testing
```bash
cd ml_service
python test_api.py
```

### System Integration Testing
```bash
cd tests
python test_system.py
```

## Project Structure

The project follows a modular architecture with clear separation of concerns:

- **Backend**: ASP.NET Core API with controllers and services
- **ML Services**: Python-based AI and machine learning services
- **Frontend**: HTML/JavaScript interface with Leaflet.js maps
- **Models**: AI model data and training results
- **Tests**: Comprehensive testing suite

## Development Status

- **Current Version**: 2.0
- **Status**: Active Development
- **Last Updated**: August 2025
- **Next Milestone**: Enhanced traffic prediction algorithms

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Developer

**Yusuf Diyar Kayir**
- GitHub: [@YusufDiyarKayir](https://github.com/YusufDiyarKayir)
- Instagram: [@YusufDiyarKayir](https://www.instagram.com/yusufdkayir/)
- LinkedIn: [Yusuf Diyar Kayir](https://linkedin.com/in/yusufdiyarkayir)

**Last Update:** August 2025
**Status:** Active Development 