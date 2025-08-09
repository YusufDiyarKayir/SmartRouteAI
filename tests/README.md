# SmartRouteAI Test System

This folder contains all test files for the SmartRouteAI project.

## File Structure

```
tests/
├── README.md              # This file
├── simple_test.py         # Simple API test
└── test_system.py         # Comprehensive test system
```

## How to Run the Test System

### 1. Using Python
```bash
cd tests
python test_system.py
```

### 2. Simple API Test
```bash
cd tests
python simple_test.py
```

## Tested Components

### System Health Checks
- **Backend Health Check**: Verifies if the ASP.NET Core API is running
- **ML Service Health Check**: Checks the status of Python Flask service
- **Model Files Check**: Verifies the existence of required AI model files

### AI Model Tests
- **AI Model Loading Test**: Checks if models are loaded successfully
- **Weather Prediction Test**: Tests ML-based weather predictions

### Functional Tests
- **Prompt Analysis Test**: Verifies correct analysis of user inputs
- **Route Optimization Test**: Tests route calculation and optimization processes
- **Performance Test**: Measures system response times
- **Error Handling Test**: Checks if error inputs are handled properly

## Test Report

After running the test system, a `test_report.json` file is created in the main directory. This file contains:

- Test results and success rates
- Error details
- Performance metrics
- Timestamps

## Requirements

### System Requirements
- Python 3.8+
- Backend must be running (http://localhost:5077)
- ML service must be running (http://localhost:5001)

### Python Packages
```bash
pip install requests
```

## Troubleshooting

### Backend Not Running
```bash
cd backend/SmartRouteAI.Backend
dotnet run
```

### ML Service Not Running
```bash
cd ml_service
python ai_service.py
```

### Missing Model Files
```bash
cd ml_service
python train_ai_models.py
```

## Test Results

The test system is considered successful when it reaches 80% success rate. For failed tests:

1. Check the `test_report.json` file
2. Review error messages
3. Ensure required services are running
4. Verify model files are present

## Continuous Testing

To run tests continuously during development:

```bash
# Windows
while ($true) { python test_system.py; Start-Sleep 300 }

# Linux/Mac
while true; do python test_system.py; sleep 300; done
```

This command runs tests every 5 minutes. 