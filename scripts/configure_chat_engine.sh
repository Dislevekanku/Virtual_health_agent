#!/bin/bash
# Configure Vertex AI Agent Builder Chat Engine
# PowerShell version for Windows

# Configuration
PROJECT_ID="ai-agent-health-assistant"
LOCATION="global"
DATASTORE_ID="clinical-guidelines-datastore"
ENGINE_ID="clinical-guidelines-chat-engine"

echo "=================================================================="
echo "CONFIGURING AGENT BUILDER CHAT ENGINE"
echo "=================================================================="

# Agent Instructions
AGENT_INSTRUCTIONS='You are a clinical triage assistant for a healthcare organization.

Your role:
- Help users understand symptom severity  
- Provide triage recommendations (emergency/urgent/routine/self-care)
- Always cite clinical guidelines using document IDs (e.g., OID-HEADACHE-001)

Red flag symptoms require IMMEDIATE escalation to emergency care.

Always be conservative - when in doubt, recommend higher level of care.

Format your responses with:
1. Clinical information based on guidelines
2. Triage level and recommendation  
3. Citation: [Document ID, Source, Section]'

echo ""
echo "Creating chat engine with datastore..."
echo "Engine ID: $ENGINE_ID"
echo "Datastore: $DATASTORE_ID"
echo ""

# Create chat engine using gcloud
gcloud alpha discovery-engine engines create \
  --engine-id="$ENGINE_ID" \
  --display-name="Clinical Guidelines Chat Engine" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" \
  --collection-id="default_collection" \
  --solution-type="SOLUTION_TYPE_CHAT" \
  --data-store-ids="$DATASTORE_ID" \
  --industry-vertical="GENERIC"

echo ""
echo "=================================================================="
echo "Engine creation started (takes 15-30 minutes)"
echo "=================================================================="
echo ""
echo "Monitor progress:"
echo "https://console.cloud.google.com/gen-app-builder/engines?project=$PROJECT_ID"
echo ""
echo "Once complete, configure model in console:"
echo "  - Model: gemini-1.5-flash"
echo "  - Temperature: 0.2"
echo "  - Enable Citations"
echo "  - Enable Grounding"
echo ""

