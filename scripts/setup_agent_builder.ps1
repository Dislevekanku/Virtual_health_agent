# Agent Builder Setup Automation Script
# This script helps automate the Agent Builder setup process

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "AGENT BUILDER SETUP AUTOMATION" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan

# Configuration
$PROJECT_ID = "ai-agent-health-assistant"
$LOCATION = "us-central1"
$GROUNDING_TOOL_URL = "https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool"
$DATASTORE_ID = "clinical-guidelines-datastore"

Write-Host "`n🎯 Configuration:" -ForegroundColor Yellow
Write-Host "   Project: $PROJECT_ID" -ForegroundColor White
Write-Host "   Location: $LOCATION" -ForegroundColor White
Write-Host "   Grounding Tool: $GROUNDING_TOOL_URL" -ForegroundColor White
Write-Host "   Datastore: $DATASTORE_ID" -ForegroundColor White

# Set credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = ".\key.json"
Write-Host "`n✓ Using credentials: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Green

Write-Host "`n📋 Manual Setup Steps:" -ForegroundColor Yellow
Write-Host "`n1. Open Agent Builder Console:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/vertex-ai/agent-builder" -ForegroundColor Cyan

Write-Host "`n2. Create or Configure Agent:" -ForegroundColor White
Write-Host "   • Name: Clinical Guidelines Assistant" -ForegroundColor Gray
Write-Host "   • Model: gemini-1.5-flash-001" -ForegroundColor Gray
Write-Host "   • Temperature: 0.2" -ForegroundColor Gray
Write-Host "   • Safety: Medical content Block Only High" -ForegroundColor Gray

Write-Host "`n3. Add System Instructions:" -ForegroundColor White
Write-Host "   You are a clinical decision support assistant that provides evidence-based" -ForegroundColor Gray
Write-Host "   information from clinical guidelines. NEVER provide definitive diagnoses." -ForegroundColor Gray

Write-Host "`n4. Integration Options:" -ForegroundColor White

Write-Host "`n   Option A - Direct Datastore Integration:" -ForegroundColor Green
Write-Host "   • Tools → Integrations → Datastores" -ForegroundColor Gray
Write-Host "   • Add Vertex AI Search datastore: $DATASTORE_ID" -ForegroundColor Gray
Write-Host "   • Enable grounding with citations" -ForegroundColor Gray

Write-Host "`n   Option B - External Tool Integration:" -ForegroundColor Green
Write-Host "   • Tools → External Tools" -ForegroundColor Gray
Write-Host "   • Add tool: $GROUNDING_TOOL_URL" -ForegroundColor Gray
Write-Host "   • Configure parameters: user_text, max_results" -ForegroundColor Gray

Write-Host "`n5. Create Medical Intents:" -ForegroundColor White
Write-Host "   • Medical Query Intent" -ForegroundColor Gray
Write-Host "   • Emergency Symptoms Intent" -ForegroundColor Gray
Write-Host "   • Configure webhook fulfillment" -ForegroundColor Gray

Write-Host "`n6. Test Integration:" -ForegroundColor White
Write-Host "   • What are red flag headache symptoms?" -ForegroundColor Gray
Write-Host "   • When should I see a doctor for nausea?" -ForegroundColor Gray
Write-Host "   • What is orthostatic hypotension?" -ForegroundColor Gray

Write-Host "`n🧪 Test Your Grounding Tool:" -ForegroundColor Yellow

try {
    $testData = @{
        user_text = "What are red flag headache symptoms?"
    } | ConvertTo-Json
    
    Write-Host "   Testing grounding tool..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "$GROUNDING_TOOL_URL/test" -Method POST -ContentType "application/json" -Body $testData -TimeoutSec 30
    
    if ($response.StatusCode -eq 200) {
        $result = $response.Content | ConvertFrom-Json
        Write-Host "   ✓ Grounding tool working" -ForegroundColor Green
        Write-Host "   Response length: $($result.answer.Length) characters" -ForegroundColor White
        Write-Host "   Citations: $($result.citations.Count)" -ForegroundColor White
        Write-Host "   Confidence: $($result.confidence)" -ForegroundColor White
    } else {
        Write-Host "   ⚠️ Grounding tool test failed: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️ Could not test grounding tool: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n📋 Validation Checklist:" -ForegroundColor Yellow
Write-Host "`n✅ Agent Configuration:" -ForegroundColor White
Write-Host "   [ ] Model: gemini-1.5-flash-001" -ForegroundColor Gray
Write-Host "   [ ] Temperature: 0.2" -ForegroundColor Gray
Write-Host "   [ ] Safety settings configured" -ForegroundColor Gray
Write-Host "   [ ] System instructions added" -ForegroundColor Gray

Write-Host "`n✅ Grounding Integration:" -ForegroundColor White
Write-Host "   [ ] Datastore connected OR external tool configured" -ForegroundColor Gray
Write-Host "   [ ] Grounding enabled" -ForegroundColor Gray
Write-Host "   [ ] Citations enabled" -ForegroundColor Gray
Write-Host "   [ ] Max results: 5" -ForegroundColor Gray

Write-Host "`n✅ Intent Configuration:" -ForegroundColor White
Write-Host "   [ ] Medical Query Intent created" -ForegroundColor Gray
Write-Host "   [ ] Emergency Symptoms Intent created" -ForegroundColor Gray
Write-Host "   [ ] Webhook fulfillment configured" -ForegroundColor Gray
Write-Host "   [ ] Training phrases added" -ForegroundColor Gray

Write-Host "`n✅ Testing:" -ForegroundColor White
Write-Host "   [ ] Medical queries return guidelines" -ForegroundColor Gray
Write-Host "   [ ] Citations appear in responses" -ForegroundColor Gray
Write-Host "   [ ] Emergency symptoms trigger warnings" -ForegroundColor Gray
Write-Host "   [ ] Medical disclaimers included" -ForegroundColor Gray

Write-Host "`n🎉 Expected Results:" -ForegroundColor Yellow
Write-Host "`nWhen working correctly, your agent should:" -ForegroundColor White
Write-Host "   • Return clinical guidelines with citations" -ForegroundColor Gray
Write-Host "   • Flag emergency symptoms appropriately" -ForegroundColor Gray
Write-Host "   • Include medical disclaimers" -ForegroundColor Gray
Write-Host "   • Provide triage recommendations" -ForegroundColor Gray

Write-Host "`n🚀 Quick Links:" -ForegroundColor Yellow
Write-Host "   Agent Builder: https://console.cloud.google.com/vertex-ai/agent-builder" -ForegroundColor Cyan
Write-Host "   Grounding Tool: $GROUNDING_TOOL_URL" -ForegroundColor Cyan
Write-Host "   Test Endpoint: $GROUNDING_TOOL_URL/test" -ForegroundColor Cyan

Write-Host "`n=================================================================================" -ForegroundColor Cyan
Write-Host "Setup complete! Follow the manual steps above to configure your agent." -ForegroundColor Green
Write-Host "=================================================================================" -ForegroundColor Cyan
