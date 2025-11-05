# Fix Webhook Integration using gcloud commands
# This script connects the RAG webhook to Dialogflow CX flow fulfillment

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "FIXING WEBHOOK INTEGRATION WITH GCLOUD" -ForegroundColor Cyan
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
    # Method 1: Try to create a medical intent with webhook
    Write-Host "`n🔧 Method 1: Creating medical intent with webhook..." -ForegroundColor Yellow
    
    # Create intent configuration file
    $intentConfig = @{
        displayName = "Medical Query Intent"
        description = "Handles medical queries and calls clinical guidelines webhook"
        trainingPhrases = @(
            @{
                parts = @(@{ text = "What are red flag headache symptoms?" })
                repeatCount = 1
            },
            @{
                parts = @(@{ text = "When should I see a doctor for nausea?" })
                repeatCount = 1
            },
            @{
                parts = @(@{ text = "What is orthostatic hypotension?" })
                repeatCount = 1
            },
            @{
                parts = @(@{ text = "Medical advice" })
                repeatCount = 1
            },
            @{
                parts = @(@{ text = "Health symptoms" })
                repeatCount = 1
            }
        )
        messages = @(
            @{
                text = @{
                    text = @("Let me search the clinical guidelines for you...")
                }
            }
        )
        webhookEnabled = $true
        webhook = $WEBHOOK_NAME
    } | ConvertTo-Json -Depth 10
    
    $intentConfig | Out-File -FilePath "medical_intent.json" -Encoding UTF8
    Write-Host "   ✓ Created medical intent configuration" -ForegroundColor Green
    
    # Create the intent
    $createIntentCmd = "& 'C:\Users\dk032\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' alpha dialogflow cx intents create --location=$LOCATION --project=$PROJECT_ID --agent=$AGENT_ID --intent-file=medical_intent.json"
    
    Write-Host "   🔄 Creating medical intent..." -ForegroundColor Yellow
    Invoke-Expression $createIntentCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Medical intent created successfully!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Medical intent creation failed, trying alternative method..." -ForegroundColor Yellow
    }
    
    # Method 2: Try to update the start page with webhook fulfillment
    Write-Host "`n🔧 Method 2: Updating start page with webhook fulfillment..." -ForegroundColor Yellow
    
    # Get current page configuration
    Write-Host "   📋 Getting current start page configuration..." -ForegroundColor Yellow
    $getPageCmd = "& 'C:\Users\dk032\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' alpha dialogflow cx pages describe $PAGE_ID --location=$LOCATION --project=$PROJECT_ID --agent=$AGENT_ID --flow=$FLOW_ID --format=json"
    
    $pageData = Invoke-Expression $getPageCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Retrieved start page configuration" -ForegroundColor Green
        
        # Create webhook fulfillment configuration
        $webhookFulfillment = @{
            webhook = $WEBHOOK_NAME
            messages = @(
                @{
                    text = @{
                        text = @("Searching clinical guidelines...")
                    }
                }
            )
        } | ConvertTo-Json -Depth 10
        
        $webhookFulfillment | Out-File -FilePath "webhook_fulfillment.json" -Encoding UTF8
        
        # Update page with webhook fulfillment
        Write-Host "   🔄 Adding webhook to entry fulfillment..." -ForegroundColor Yellow
        $updatePageCmd = "& 'C:\Users\dk032\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' alpha dialogflow cx pages update $PAGE_ID --location=$LOCATION --project=$PROJECT_ID --agent=$AGENT_ID --flow=$FLOW_ID --entry-fulfillment-webhook=$WEBHOOK_NAME"
        
        Invoke-Expression $updatePageCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Successfully added webhook to entry fulfillment!" -ForegroundColor Green
            Write-Host "   Webhook: $WEBHOOK_NAME" -ForegroundColor White
            Write-Host "   Page: Start Page" -ForegroundColor White
        } else {
            Write-Host "   ⚠️ Page update failed" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ Failed to get start page configuration" -ForegroundColor Red
    }
    
    # Method 3: Try to create a route with webhook
    Write-Host "`n🔧 Method 3: Creating medical route..." -ForegroundColor Yellow
    
    # Create route configuration
    $routeConfig = @{
        intent = "projects/$PROJECT_ID/locations/$LOCATION/agents/$AGENT_ID/intents/MEDICAL_QUERY_INTENT"
        condition = "true"
        triggerFulfillment = @{
            webhook = $WEBHOOK_NAME
            messages = @(
                @{
                    text = @{
                        text = @("Let me search the clinical guidelines for you...")
                    }
                }
            )
        }
    } | ConvertTo-Json -Depth 10
    
    $routeConfig | Out-File -FilePath "medical_route.json" -Encoding UTF8
    Write-Host "   ✓ Created medical route configuration" -ForegroundColor Green
    
    # Clean up temporary files
    Remove-Item "medical_intent.json" -ErrorAction SilentlyContinue
    Remove-Item "webhook_fulfillment.json" -ErrorAction SilentlyContinue
    Remove-Item "medical_route.json" -ErrorAction SilentlyContinue
    
    Write-Host "`n🎉 WEBHOOK INTEGRATION FIX ATTEMPTED!" -ForegroundColor Cyan
    Write-Host "=================================================================================" -ForegroundColor Cyan
    
    Write-Host "`n✅ Attempted fixes:" -ForegroundColor Green
    Write-Host "   • Created medical intent with webhook" -ForegroundColor White
    Write-Host "   • Added webhook to entry fulfillment" -ForegroundColor White
    Write-Host "   • Created medical route configuration" -ForegroundColor White
    
    Write-Host "`n🧪 Test in Preview panel:" -ForegroundColor Yellow
    Write-Host "   Query: 'What are red flag headache symptoms?'" -ForegroundColor White
    Write-Host "   Expected: Clinical guidelines response with citations" -ForegroundColor White
    
    Write-Host "`n📋 If still not working, manual steps:" -ForegroundColor Yellow
    Write-Host "   1. Go to Build → Default Start Flow → Start Page" -ForegroundColor White
    Write-Host "   2. Add webhook to Entry fulfillment" -ForegroundColor White
    Write-Host "   3. Or create a medical intent with webhook" -ForegroundColor White
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n📋 Please try manual integration steps:" -ForegroundColor Yellow
    Write-Host "   1. Go to Build → Default Start Flow → Start Page" -ForegroundColor White
    Write-Host "   2. Add webhook to Entry fulfillment" -ForegroundColor White
}

Write-Host "`n=================================================================================" -ForegroundColor Cyan
