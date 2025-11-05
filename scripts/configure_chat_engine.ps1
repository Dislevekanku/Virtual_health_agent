# Configure Vertex AI Agent Builder Chat Engine
# PowerShell script for Windows

$PROJECT_ID = "ai-agent-health-assistant"
$LOCATION = "global"
$DATASTORE_ID = "clinical-guidelines-datastore"
$ENGINE_ID = "clinical-guidelines-chat-engine"
$GCLOUD = "C:\Users\dk032\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

Write-Host "=" -NoNewline
Write-Host ("=" * 79)
Write-Host "CONFIGURING AGENT BUILDER CHAT ENGINE"
Write-Host "=" -NoNewline
Write-Host ("=" * 79)
Write-Host ""

Write-Host "Creating chat engine..."
Write-Host "  Engine ID: $ENGINE_ID"
Write-Host "  Datastore: $DATASTORE_ID"
Write-Host ""

# Create chat engine using gcloud alpha
& $GCLOUD alpha discovery-engine engines create `
  --engine-id="$ENGINE_ID" `
  --display-name="Clinical Guidelines Chat Engine" `
  --location="$LOCATION" `
  --project="$PROJECT_ID" `
  --collection-id="default_collection" `
  --solution-type="SOLUTION_TYPE_CHAT" `
  --data-store-ids="$DATASTORE_ID" `
  --industry-vertical="GENERIC"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" -NoNewline
    Write-Host ("=" * 79)
    Write-Host "✅ ENGINE CREATION STARTED"
    Write-Host "=" -NoNewline
    Write-Host ("=" * 79)
    Write-Host ""
    Write-Host "⏳ This takes 15-30 minutes to complete"
    Write-Host ""
    Write-Host "📊 Monitor progress:"
    Write-Host "   https://console.cloud.google.com/gen-app-builder/engines?project=$PROJECT_ID"
    Write-Host ""
    Write-Host "⚙️  Once complete, configure in console:"
    Write-Host "   1. Click on engine: $ENGINE_ID"
    Write-Host "   2. Go to 'Configurations' or 'Edit'"
    Write-Host "   3. Set Model: gemini-1.5-flash"
    Write-Host "   4. Set Temperature: 0.2"
    Write-Host "   5. Enable ✓ Citations"
    Write-Host "   6. Enable ✓ Grounding"
    Write-Host "   7. Add Agent Instructions (see below)"
    Write-Host ""
    Write-Host "📝 Agent Instructions to add:"
    Write-Host "=" -NoNewline
    Write-Host ("=" * 79)
    Write-Host @"
You are a clinical triage assistant for a healthcare organization.

Your role:
- Help users understand symptom severity
- Provide triage recommendations (emergency/urgent/routine/self-care)
- Always cite clinical guidelines using document IDs (e.g., OID-HEADACHE-001)

Red flag symptoms require IMMEDIATE escalation to emergency care.

Always be conservative - when in doubt, recommend higher level of care.

Format your responses with:
1. Clinical information based on guidelines
2. Triage level (Emergency/Urgent/Routine/Self-care) and recommendation
3. Citation: [Document ID, Source, Section]

Example:
"According to the Headache Evaluation Guideline (OID-HEADACHE-001):
Thunderclap headache requires IMMEDIATE emergency evaluation.
Triage: EMERGENCY - Call 911.
[Citation: OID-HEADACHE-001, Internal Clinical SOP, Red Flags]"
"@
    Write-Host ""
    Write-Host "=" -NoNewline
    Write-Host ("=" * 79)
    Write-Host ""
    Write-Host "🧪 Test Query (once ready):"
    Write-Host '   "What are red flag headache symptoms?"'
    Write-Host ""
    Write-Host "Expected: Should cite OID-HEADACHE-001 with thunderclap, vision changes, etc."
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Command failed or engine already exists"
    Write-Host ""
    Write-Host "Check existing engines:"
    Write-Host "  https://console.cloud.google.com/gen-app-builder/engines?project=$PROJECT_ID"
    Write-Host ""
    Write-Host "Or try creating via console:"
    Write-Host "  1. Go to: https://console.cloud.google.com/gen-app-builder/engines?project=$PROJECT_ID"
    Write-Host "  2. Click 'CREATE APP'"
    Write-Host "  3. Select 'Chat'"
    Write-Host "  4. Follow wizard to connect datastore"
    Write-Host ""
}

