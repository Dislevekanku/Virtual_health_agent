# 🎯 Manual Webhook Integration Guide

## ✅ Your Webhook is Ready!

**Webhook URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/webhook`

## 🔧 Step-by-Step Integration

### Step 1: Go to Dialogflow CX Agent

**Direct Link**: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

### Step 2: Navigate to the Flow

1. **Click on "Build" tab** (left sidebar)
2. **Click on "Default Start Flow"** (in the flows list)
3. **Click on "Start Page"** (the first page in the flow)

### Step 3: Add Webhook Fulfillment

1. **Scroll down to "Entry fulfillment"** section
2. **Click "+ Add dialogue option"**
3. **Select "Call webhook"** from the dropdown
4. **In the webhook field, type**: `clinical-guidelines-webhook`
5. **Click "Save"** (top right)

### Step 4: Test the Integration

1. **Click on "Preview" panel** (right side of the screen)
2. **Type a test query**: `What are red flag headache symptoms?`
3. **Press Enter**
4. **Expected result**: Clinical guidelines with citations and red flag warnings

## 🧪 Test Queries

Try these queries in the Preview panel:

1. **Red Flag Test**: `What are red flag headache symptoms?`
   - Should return: Thunderclap headache, vision changes, neurological deficits

2. **Triage Test**: `When should someone with nausea see a doctor urgently?`
   - Should return: Persistent vomiting >24 hours, dehydration signs

3. **Specific Condition**: `What is orthostatic hypotension?`
   - Should return: BP drop ≥20/10 mmHg, symptoms, management

4. **Citation Test**: `What guidelines cover dizziness and vertigo?`
   - Should return: Document IDs like `[OID-NEURO-DIZZY-003]`

## 📋 Expected Response Format

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

## 🔍 What the Webhook Does

Your webhook automatically:

1. **Receives queries** from Dialogflow CX
2. **Searches** the clinical-guidelines-datastore
3. **Detects red flags** (emergency symptoms)
4. **Provides triage recommendations**:
   - 🚨 **Emergency**: Immediate medical attention required
   - ⚡ **Urgent**: Same-day evaluation needed
   - 📋 **Routine**: Standard care appropriate
5. **Returns citations** with document IDs
6. **Formats responses** for clinical use

## 🚨 Red Flag Detection

The webhook automatically detects:

**Emergency Symptoms**:
- Thunderclap headache
- Vision changes
- Neurological deficits
- Chest pain
- Shortness of breath
- Loss of consciousness

**Urgent Symptoms**:
- Persistent vomiting
- Severe dehydration
- Fever with confusion
- Severe weakness
- Unintentional weight loss

## 🛠️ Troubleshooting

### If the webhook doesn't work:

1. **Check webhook name**: Make sure you typed `clinical-guidelines-webhook` exactly
2. **Verify webhook exists**: Go to **Manage** → **Webhooks** to confirm it's there
3. **Check function logs**: Go to Cloud Functions console to see any errors
4. **Test webhook directly**: Use the test endpoint to verify it works

### Test Endpoints:

- **Health Check**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/health`
- **Direct Test**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/test`

### Direct Test Command:
```bash
curl -X POST https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/test \
  -H "Content-Type: application/json" \
  -d '{"query": "What are red flag headache symptoms?"}'
```

## 🎉 Success Indicators

You'll know it's working when:

✅ **Queries return clinical information**  
✅ **Citations appear** (e.g., `[OID-NEURO-HEAD-001]`)  
✅ **Red flag warnings** show for emergency symptoms  
✅ **Triage recommendations** are provided  
✅ **Responses are evidence-based** and medical  

## 🚀 Next Steps

Once integrated and tested:

1. **Share the agent** with your team
2. **Create additional flows** for specific use cases
3. **Add more clinical guidelines** to the knowledge base
4. **Integrate with your existing systems**

## 📞 Support

If you encounter issues:

1. **Check the Cloud Function logs** for errors
2. **Verify the webhook configuration** in Dialogflow CX
3. **Test the webhook directly** using the test endpoints
4. **Ensure the datastore is accessible** and contains data

---

**Your clinical guidelines agent is now ready for use!** 🎯