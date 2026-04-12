# ==============================================================================
# PIPELINE DE MOBILE DEVOPS (FIREBASE APP DISTRIBUTION)
# ==============================================================================
param (
    [string]$AppId = ""
)

Write-Host "🔥 INICIANDO EMPAQUETADO PARA PRODUCCIÓN (FLUTTER) 🔥" -ForegroundColor Cyan

if ($AppId -eq "") {
    Write-Host "⚠️ ADVERTENCIA: Debes pasar tu APP ID de Firebase como parámetro." -ForegroundColor Yellow
    Write-Host "Ejemplo: .\distribute.ps1 -AppId `"1:1234567890:android:34985734985734`"" -ForegroundColor Yellow
    exit
}

Write-Host "1. Compilando el código fuente en un APK Release. Por favor espera..."
flutter clean
flutter build apk --release

$apkPath = "build\app\outputs\flutter-apk\app-release.apk"

if (Test-Path $apkPath) {
    Write-Host "✅ APK construida exitosamente en: $apkPath" -ForegroundColor Green
    Write-Host "2. Subiendo a Firebase App Distribution..."
    
    # Este comando asume que tienes 'firebase-tools' instalado globalmente en npm
    firebase appdistribution:distribute $apkPath --app $AppId --groups "testers"
    
    Write-Host "🎉 PROCESO FINALIZADO. Revisa tu correo de Tester en el celular." -ForegroundColor Green
} else {
    Write-Host "❌ Error: La compilación del APK falló." -ForegroundColor Red
}
