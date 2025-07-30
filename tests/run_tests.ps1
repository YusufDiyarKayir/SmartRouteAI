# SmartRouteAI Test Sistemi Çalıştırıcı
# Bu script tüm projeyi test eder

Write-Host "🚀 SmartRouteAI Test Sistemi Başlatılıyor..." -ForegroundColor Green
Write-Host "🕒 Başlangıç: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan

# Ana dizine geç
Set-Location ..

# Python'un yüklü olup olmadığını kontrol et
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python bulundu: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python bulunamadı! Lütfen Python'u yükleyin." -ForegroundColor Red
    exit 1
}

# Gerekli Python paketlerini kontrol et
Write-Host "📦 Python paketleri kontrol ediliyor..." -ForegroundColor Yellow

$requiredPackages = @("requests", "json", "datetime")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "   ✅ $package" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ $package eksik" -ForegroundColor Red
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "❌ Eksik paketler: $($missingPackages -join ', ')" -ForegroundColor Red
    Write-Host "💡 Lütfen şu komutu çalıştırın: pip install $($missingPackages -join ' ')" -ForegroundColor Yellow
    exit 1
}

# Backend'in çalışıp çalışmadığını kontrol et
Write-Host "🔍 Backend kontrol ediliyor..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:5077/api/route/health" -TimeoutSec 5 -ErrorAction Stop
    if ($backendResponse.StatusCode -eq 200) {
        Write-Host "✅ Backend çalışıyor" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend yanıt veriyor ama durum kodu: $($backendResponse.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend çalışmıyor veya erişilemiyor" -ForegroundColor Red
    Write-Host "💡 Backend'i başlatmak için: cd backend/SmartRouteAI.Backend && dotnet run" -ForegroundColor Yellow
}

# ML servisinin çalışıp çalışmadığını kontrol et
Write-Host "🔍 ML Servisi kontrol ediliyor..." -ForegroundColor Yellow
try {
    $mlResponse = Invoke-WebRequest -Uri "http://localhost:5001/health" -TimeoutSec 5 -ErrorAction Stop
    if ($mlResponse.StatusCode -eq 200) {
        Write-Host "✅ ML Servisi çalışıyor" -ForegroundColor Green
    } else {
        Write-Host "⚠️ ML Servisi yanıt veriyor ama durum kodu: $($mlResponse.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ ML Servisi çalışmıyor veya erişilemiyor" -ForegroundColor Red
    Write-Host "💡 ML Servisini başlatmak için: cd ml_service && python start_ai_service.py" -ForegroundColor Yellow
}

# Model dosyalarının varlığını kontrol et
Write-Host "📁 Model dosyaları kontrol ediliyor..." -ForegroundColor Yellow
$modelFiles = @(
    "models/traffic_prediction_model.h5",
    "models/traffic_prediction_scaler.pkl",
    "models/route_optimization_model.h5",
    "models/weather_model.pkl"
)

$existingModels = 0
foreach ($model in $modelFiles) {
    if (Test-Path $model) {
        $existingModels++
        Write-Host "   ✅ $model" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $model" -ForegroundColor Red
    }
}

if ($existingModels -eq 0) {
    Write-Host "⚠️ Hiç model dosyası bulunamadı!" -ForegroundColor Yellow
    Write-Host "💡 Modelleri eğitmek için: cd ml_service && python train_ai_models.py" -ForegroundColor Yellow
}

# Test sistemini çalıştır
Write-Host "🧪 Test sistemi başlatılıyor..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

try {
    python tests/test_system.py
    $testExitCode = $LASTEXITCODE
    
    if ($testExitCode -eq 0) {
        Write-Host "🎉 Tüm testler başarıyla tamamlandı!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Bazı testler başarısız oldu. test_report.json dosyasını kontrol edin." -ForegroundColor Yellow
    }
} catch {
    Write-Host "💥 Test sistemi çalıştırılırken hata oluştu: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🕒 Bitiş: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan

# Test raporunu göster
if (Test-Path "test_report.json") {
    Write-Host "📊 Test raporu oluşturuldu: test_report.json" -ForegroundColor Green
    
    try {
        $report = Get-Content "test_report.json" | ConvertFrom-Json
        Write-Host "📈 Başarı Oranı: $($report.success_rate)%" -ForegroundColor Cyan
        Write-Host "✅ Başarılı Test: $($report.successful_tests)/$($report.total_tests)" -ForegroundColor Cyan
    } catch {
        Write-Host "⚠️ Rapor okunamadı" -ForegroundColor Yellow
    }
}

Write-Host "🏁 Test sistemi tamamlandı!" -ForegroundColor Green 