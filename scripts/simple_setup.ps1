# Simple Agent Builder Setup Guide

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "AGENT BUILDER SETUP GUIDE" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan

$PROJECT_ID = "ai-agent-health-assistant"
$GROUNDING_TOOL_URL = "https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool"

Write-Host "`n🎯 Your Grounding Tool is Ready!" -ForegroundColor Green
Write-Host "   URL: $GROUNDING_TOOL_URL" -ForegroundColor White

Write-Host "`n📋 Manual Setup Steps (10-30 minutes):" -ForegroundColor Yellow

Write-Host "`n1. Open Agent Builder:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/vertex-ai/agent-builder" -ForegroundColor Cyan

Write-Host "`n2. Create/Configure Agent:" -ForegroundColor White
Write-Host "   • Name: Clinical Guidelines Assistant" -ForegroundColor Gray
Write-Host "   • Model: gemini-1.5-flash-001" -ForegroundColor Gray
Write-Host "   • Temperature: 0.2" -ForegroundColor Gray

Write-Host "`n3. Add System Instructions:" -ForegroundColor White
Write-Host "   You are a clinical decision support assistant..." -ForegroundColor Gray

Write-Host "`n4. Integration Options:" -ForegroundColor White
Write-Host "   Option A: Tools → Integrations → Datastores" -ForegroundColor Green
Write-Host "   Option B: Tools → External Tools → Add $GROUNDING_TOOL_URL" -ForegroundColor Green

Write-Host "`n5. Create Medical Intents:" -ForegroundColor White
Write-Host "   • Medical Query Intent" -ForegroundColor Gray
Write-Host "   • Emergency Symptoms Intent" -ForegroundColor Gray

Write-Host "`n6. Test with:" -ForegroundColor White
Write-Host "   • What are red flag headache symptoms?" -ForegroundColor Gray
Write-Host "   • When should I see a doctor for nausea?" -ForegroundColor Gray

Write-Host "`n🧪 Testing Grounding Tool..." -ForegroundColor Yellow

try {
    $testData = '{"user_text": "What are red flag headache symptoms?"}'
    $response = Invoke-WebRequest -Uri "$GROUNDING_TOOL_URL/test" -Method POST -ContentType "application/json" -Body $testData -TimeoutSec 30
    
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Grounding tool is working!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Grounding tool test failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️ Could not test grounding tool" -ForegroundColor Yellow
}

Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
Write-Host "   Follow the detailed guide in COMPLETE_AGENT_BUILDER_SETUP.md" -ForegroundColor White

Write-Host "`n=================================================================================" -ForegroundColor Cyan
