# SmartRouteAI - Advanced ML Tabanli Hava Durumu Sistemi Baslatma
Write-Host "SmartRouteAI - Advanced ML Tabanli Hava Durumu Sistemi" -ForegroundColor Cyan

# 1. ML Modelleri Kontrolu
Write-Host "ML Modelleri Kontrolu..." -ForegroundColor Yellow
Set-Location "ml_service"

# Python bagimliliklari kontrolu (sadece gerekirse yukle)
Write-Host "Python bagimliliklari kontrol ediliyor..." -ForegroundColor Yellow
$pythonCheck = python -c "import flask, sklearn, pandas, numpy, joblib" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Tum bagimliliklar mevcut" -ForegroundColor Green
} else {
    Write-Host "[WARN] Bazi bagimliliklar eksik, yukleniyor..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# ML modelleri kontrolu - yeni model dosyalarini kontrol et
$modelsPath = "../models"
$trafficModelPath = "$modelsPath/traffic_prediction_model.pkl"
$trafficScalerPath = "$modelsPath/traffic_prediction_scaler.pkl"
$trafficMetadataPath = "$modelsPath/traffic_prediction_metadata.json"
$routeModelPath = "$modelsPath/route_optimization_duration_model.pkl"
$routeScalerPath = "$modelsPath/route_optimization_scaler.pkl"
$routeMetadataPath = "$modelsPath/route_optimization_metadata.json"

$allModelsExist = (Test-Path $trafficModelPath) -and (Test-Path $trafficScalerPath) -and (Test-Path $trafficMetadataPath) -and (Test-Path $routeModelPath) -and (Test-Path $routeScalerPath) -and (Test-Path $routeMetadataPath)

if (-not $allModelsExist) {
    Write-Host "ML modelleri bulunamadi! Model egitimi baslatiliyor..." -ForegroundColor Yellow
    $trainingOutput = python train_ai_models.py 2>&1
    Write-Host $trainingOutput
    
    # Egitim verisi sayisini cikar
    if ($trainingOutput -like "*veri noktasi olusturuldu*") {
        $lines = $trainingOutput -split "`n"
        foreach ($line in $lines) {
            if ($line -like "*veri noktasi olusturuldu*") {
                $parts = $line -split " "
                foreach ($part in $parts) {
                    if ($part -match "^\d+$") {
                        $global:TrainingDataCount = $part
                        break
                    }
                }
                break
            }
        }
    }
} else {
    Write-Host "[OK] ML modelleri mevcut, egitim atlaniyor" -ForegroundColor Green
    
    # Mevcut modeller icin egitim verisi sayisini oku
    $trainingResultsPath = "../models/training_results.json"
    if (Test-Path $trainingResultsPath) {
        try {
            $trainingResults = Get-Content $trainingResultsPath | ConvertFrom-Json
            $global:TrainingDataCount = $trainingResults.data_points
        } catch {
            $global:TrainingDataCount = "Bilinmiyor"
        }
    } else {
        $global:TrainingDataCount = "Bilinmiyor"
    }
}

# 2. Advanced Hava Durumu Servisi Baslat
Write-Host "Advanced Hava Durumu Servisi baslatiliyor..." -ForegroundColor Yellow
Start-Process python -ArgumentList "advanced_weather_predictor.py" -WindowStyle Hidden
Start-Sleep -Seconds 8

# 3. Backend'i Baslat
Write-Host "Backend Baslatiliyor..." -ForegroundColor Yellow
Set-Location "../backend/SmartRouteAI.Backend"

# Projeyi derle ve baslat
Write-Host "Backend derleniyor..." -ForegroundColor Yellow
dotnet build
if ($LASTEXITCODE -eq 0) {
    Write-Host "Backend baslatiliyor..." -ForegroundColor Green
    Start-Process dotnet -ArgumentList "run" -WindowStyle Hidden
    Start-Sleep -Seconds 10
} else {
    Write-Host "Backend derleme hatasi!" -ForegroundColor Red
    exit 1
}

# 5. Frontend'i Ac
Write-Host "Frontend Aciliyor..." -ForegroundColor Yellow
Start-Process "http://localhost:5077"

# 6. Servis Durumu
Write-Host "Servis Durumu:" -ForegroundColor Cyan
Write-Host "Advanced Hava Durumu: http://localhost:5001" -ForegroundColor Green
Write-Host "Backend:        http://localhost:5077" -ForegroundColor Green
Write-Host "Frontend:       http://localhost:5077" -ForegroundColor Green

Write-Host "Tum servisler basariyla baslatildi!" -ForegroundColor Green
Write-Host "Advanced ML tabanli hava durumu sistemi kullanima hazir!" -ForegroundColor Cyan

# Servisleri durdurmak icin bilgi
Write-Host "Servisleri durdurmak icin:" -ForegroundColor Yellow
Write-Host "   Get-Process python,dotnet | Stop-Process -Force" -ForegroundColor Gray
Write-Host "   veya: taskkill /f /im python.exe & taskkill /f /im dotnet.exe" -ForegroundColor Gray

Write-Host "Servisler calismaya devam ediyor..." -ForegroundColor Yellow

# Egitim verisi sayisini goster
if ($global:TrainingDataCount) {
    Write-Host "[DATA] Egitim Verisi: $($global:TrainingDataCount) veri noktasi" -ForegroundColor Magenta
} else {
    Write-Host "[DATA] Egitim Verisi: Bilinmiyor" -ForegroundColor Magenta
} 