# Deploy simplified-rag-webhook Cloud Function
# PowerShell script for Windows

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Deploying Simplified RAG Webhook to Cloud Functions" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Host "[ERROR] gcloud CLI not found. Please install Google Cloud SDK." -ForegroundColor Red
    Write-Host "  Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ gcloud CLI found" -ForegroundColor Green
Write-Host ""

# Set project
Write-Host "Setting project..." -ForegroundColor Yellow
gcloud config set project ai-agent-health-assistant

# Deploy the function
Write-Host ""
Write-Host "Deploying Cloud Function..." -ForegroundColor Yellow
Write-Host "  Function: simplified-rag-webhook" -ForegroundColor White
Write-Host "  Runtime: python311" -ForegroundColor White
Write-Host "  Trigger: HTTP" -ForegroundColor White
Write-Host "  Source: ." -ForegroundColor White
Write-Host ""

gcloud functions deploy simplified-rag-webhook `
    --gen2 `
    --runtime=python311 `
    --region=us-central1 `
    --source=. `
    --entry-point=app `
    --trigger-http `
    --allow-unauthenticated `
    --memory=1GB `
    --timeout=540s `
    --max-instances=10

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Webhook URL:" -ForegroundColor Cyan
    gcloud functions describe simplified-rag-webhook --gen2 --region=us-central1 --format="value(serviceConfig.uri)"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Test the webhook using test_webhook.py" -ForegroundColor White
    Write-Host "  2. The webhook will now provide improved fallback responses" -ForegroundColor White
    Write-Host "  3. Once datastore is created, it will use clinical guidelines" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "❌ DEPLOYMENT FAILED" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Not authenticated: Run 'gcloud auth login'" -ForegroundColor White
    Write-Host "  2. Missing permissions: Check IAM roles" -ForegroundColor White
    Write-Host "  3. API not enabled: Enable Cloud Functions API" -ForegroundColor White
    Write-Host ""
}

