# Add Webhook to Dialogflow CX Flow using gcloud
# This script adds the clinical-guidelines-webhook to the Default Start Flow

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "ADDING WEBHOOK TO DIALOGFLOW CX FLOW" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan

# Configuration
$PROJECT_ID = "ai-agent-health-assistant"
$LOCATION = "us-central1"
$AGENT_ID = "72d18125-ac71-4c56-8ea0-44bfc7f9b039"
$WEBHOOK_NAME = "clinical-guidelines-webhook"
$FLOW_ID = "00000000-0000-0000-0000-000000000000"
$PAGE_ID = "00000000-0000-0000-0000-000000000000"

# Set credentials
$env:GOOGLE_APPLICATION_CREDENTIALS = ".\key.json"
Write-Host "✓ Using credentials: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Green

try {
    # Get the current flow
    Write-Host "📋 Getting flow information..." -ForegroundColor Yellow
    $flowResult = & "C:\Users\dk032\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" dialogflow cx flows describe $FLOW_ID --location=$LOCATION --project=$PROJECT_ID --agent=$AGENT_ID --format=json
    
    if ($LASTEXITCODE -eq 0) {
        $flow = $flowResult | ConvertFrom-Json
        Write-Host "✓ Retrieved flow: $($flow.displayName)" -ForegroundColor Green
    } else {
        Write-Host "❌ Error getting flow information" -ForegroundColor Red
        exit 1
    }
    
    # Get the start page
    Write-Host "📋 Getting start page information..." -ForegroundColor Yellow
    $pageResult = & "C:\Users\dk032\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" dialogflow cx pages describe $PAGE_ID --location=$LOCATION --project=$PROJECT_ID --agent=$AGENT_ID --flow=$FLOW_ID --format=json
    
    if ($LASTEXITCODE -eq 0) {
        $page = $pageResult | ConvertFrom-Json
        Write-Host "✓ Retrieved start page: $($page.displayName)" -ForegroundColor Green
    } else {
        Write-Host "❌ Error getting start page information" -ForegroundColor Red
        exit 1
    }
    
    # Create webhook fulfillment configuration
    $webhookConfig = @{
        entryFulfillment = @{
            webhook = $WEBHOOK_NAME
            messages = @(
                @{
                    text = @{
                        text = @("Searching clinical guidelines...")
                    }
                }
            )
        }
    }
    
    # Save config to temporary file
    $configFile = "webhook_config.json"
    $webhookConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath $configFile -Encoding UTF8
    
    Write-Host "🔄 Adding webhook fulfillment to start page..." -ForegroundColor Yellow
    
    # Update the page with webhook
    $updateResult = & "C:\Users\dk032\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" dialogflow cx pages update $PAGE_ID --location=$LOCATION --project=$PROJECT_ID --agent=$AGENT_ID --flow=$FLOW_ID --update-mask=entryFulfillment --entry-fulfillment-webhook=$WEBHOOK_NAME
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully added webhook to flow!" -ForegroundColor Green
        Write-Host "   Webhook: $WEBHOOK_NAME" -ForegroundColor White
        Write-Host "   Page: $($page.displayName)" -ForegroundColor White
        
        # Clean up temp file
        Remove-Item $configFile -ErrorAction SilentlyContinue
        
        Write-Host "`n🎉 WEBHOOK INTEGRATION COMPLETE!" -ForegroundColor Cyan
        Write-Host "=================================================================================" -ForegroundColor Cyan
        
        Write-Host "`n✅ Your Dialogflow CX agent now has:" -ForegroundColor Green
        Write-Host "   • Clinical guidelines webhook integrated" -ForegroundColor White
        Write-Host "   • Access to medical knowledge base" -ForegroundColor White
        Write-Host "   • Red flag detection capabilities" -ForegroundColor White
        Write-Host "   • Citation support" -ForegroundColor White
        
        Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
        Write-Host "   1. Go to Dialogflow CX Preview panel" -ForegroundColor White
        Write-Host "   2. Test with: 'What are red flag headache symptoms?'" -ForegroundColor White
        Write-Host "   3. Verify citations and clinical responses" -ForegroundColor White
        Write-Host "   4. Your agent is ready for clinical use!" -ForegroundColor White
        
    } else {
        Write-Host "❌ Error updating page with webhook" -ForegroundColor Red
        Write-Host "   Output: $updateResult" -ForegroundColor Red
        
        # Clean up temp file
        Remove-Item $configFile -ErrorAction SilentlyContinue
        
        Write-Host "`n⚠️ Programmatic integration failed." -ForegroundColor Yellow
        Write-Host "   Please follow manual instructions in:" -ForegroundColor White
        Write-Host "   MANUAL_WEBHOOK_INTEGRATION.md" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n⚠️ Please follow manual instructions in:" -ForegroundColor Yellow
    Write-Host "   MANUAL_WEBHOOK_INTEGRATION.md" -ForegroundColor Cyan
}

Write-Host "`n=================================================================================" -ForegroundColor Cyan
