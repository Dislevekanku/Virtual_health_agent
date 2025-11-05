# 🎯 Dialogflow CX Integration with Clinical Guidelines Webhook

## ✅ Cloud Function Deployed Successfully!

**Webhook URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/webhook`

## 🔧 Integration Steps

### Step 1: Configure Webhook in Dialogflow CX

1. **Go to Dialogflow CX Agent**:
   - URL: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

2. **Navigate to Webhooks**:
   - Go to **Manage** → **Webhooks**
   - Click **"+ Create Webhook"**

3. **Configure Webhook**:
   - **Webhook name**: `clinical-guidelines-webhook`
   - **Webhook URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/webhook`
   - **Authentication**: None (unauthenticated)
   - Click **"Save"**

### Step 2: Add Webhook to Flow

1. **Go to Build Tab**:
   - Click **"Default Start Flow"**
   - Click on **"Start Page"**

2. **Configure Fulfillment**:
   - In the **"Fulfillment"** section
   - Click **"+ Add dialogue option"**
   - Select **"Call webhook"**
   - Select: `clinical-guidelines-webhook`
   - Click **"Save"**

### Step 3: Test Integration

1. **Go to Preview Panel** (right side)
2. **Type test queries**:
   - `What are red flag headache symptoms?`
   - `When should someone with nausea see a doctor?`
   - `What is orthostatic hypotension?`

3. **Expected Results**:
   - Clinical guidelines with citations
   - Triage recommendations (emergency/urgent/routine)
   - Document IDs like `[OID-NEURO-HEAD-001]`

## 🧪 Test Endpoints

- **Health Check**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/health`
- **Direct Test**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/test`
- **Webhook**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/webhook`

## 🔍 What the Webhook Does

1. **Receives queries** from Dialogflow CX
2. **Searches** the clinical-guidelines-datastore
3. **Returns formatted responses** with:
   - Clinical information
   - Citations with document IDs
   - Triage recommendations
   - Red flag warnings

## 🚨 Red Flag Detection

The webhook automatically detects emergency symptoms:
- **Emergency**: Thunderclap headache, vision changes, neurological deficits
- **Urgent**: Persistent vomiting, severe dehydration, fever with confusion
- **Routine**: General symptoms without red flags

## 📋 Example Response Format

```
🚨 EMERGENCY: Based on the symptoms described, immediate medical attention is required.

Based on clinical guidelines:

1. Thunderclap headache (worst headache of life) requires immediate evaluation for subarachnoid hemorrhage.

2. Visual changes with headache may indicate increased intracranial pressure.

Sources:
• [OID-NEURO-HEAD-001] OID-Headache-Guideline
• [OID-NEURO-HEAD-002] Red Flag Symptoms Protocol

⚠️ This information is for educational purposes only and does not replace professional medical advice.
```

## 🛠️ Troubleshooting

If the webhook doesn't work:

1. **Check Function Logs**:
   - Go to Cloud Functions console
   - Click on `clinical-guidelines-webhook`
   - Check logs for errors

2. **Verify Permissions**:
   - Ensure the function has access to Vertex AI Search
   - Check service account permissions

3. **Test Directly**:
   - Use the test endpoint to verify search functionality
   - Check if the datastore is accessible

## 🎉 Success!

Once configured, your Dialogflow CX agent will have access to clinical guidelines and can provide evidence-based medical information with proper citations!

---

**Next Steps**: Test the integration and verify that clinical queries return appropriate guidelines with citations.
