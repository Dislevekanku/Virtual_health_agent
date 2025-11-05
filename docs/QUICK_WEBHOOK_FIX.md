# 🚀 Quick Webhook Fix - Manual Steps

## **The Problem**
Your webhook exists but isn't connected to the flow, so medical queries get "Sorry, can you say that again?" instead of calling your RAG webhook.

## **The Solution (2 minutes)**

### **Step 1: Go to Build Tab**
1. In your Dialogflow CX console
2. Click **"Build"** tab (left sidebar)

### **Step 2: Open Default Start Flow**
1. Click **"Default Start Flow"** in the flows list
2. Click **"Start Page"** (the first page)

### **Step 3: Add Webhook to Entry Fulfillment**
1. **Scroll down** to find the **"Entry fulfillment"** section
2. Click **"+ Add fulfillment"** or **"+ Add dialogue option"**
3. Select **"Call webhook"**
4. Choose: `clinical-guidelines-webhook`
5. Click **"Save"**

## **Alternative: Create Medical Intent**

If Entry fulfillment doesn't work:

### **Step 1: Create Intent**
1. **Build Tab → Intents → "+ Create Intent"**
2. **Intent Name**: `Medical Query Intent`

### **Step 2: Add Training Phrases**
```
What are red flag headache symptoms?
When should I see a doctor for nausea?
What is orthostatic hypotension?
Medical advice
Health symptoms
Clinical guidelines
```

### **Step 3: Enable Webhook**
1. Scroll down to **"Fulfillment"** section
2. Enable **"Enable webhook call for this intent"**
3. Select: `clinical-guidelines-webhook`
4. Click **"Save"**

## **Test the Fix**

1. Go to **Preview panel** (right side)
2. Type: `What are red flag headache symptoms?`
3. **Expected**: Clinical guidelines response with citations
4. **Not Expected**: "Sorry, can you say that again?"

## **Success Indicators**

✅ **Webhook is working if you see:**
- Clinical guidelines information
- Citations like `[OID-NEURO-HEAD-001]`
- Triage recommendations (Emergency/Urgent/Routine)
- Medical disclaimers

❌ **Still broken if you see:**
- "Sorry, can you say that again?"
- Generic responses
- No clinical guidelines

## **Your Webhook URL**
`https://us-central1-ai-agent-health-assistant.cloudfunctions.net/simplified-rag-webhook/webhook`

## **Troubleshooting**

### **If webhook still not called:**
1. Check webhook exists in **Manage → Webhooks**
2. Verify webhook name is exactly: `clinical-guidelines-webhook`
3. Ensure fulfillment is enabled
4. Try creating a new intent with webhook

### **If webhook called but errors:**
1. Check Cloud Function logs
2. Test webhook directly: `/test` endpoint
3. Verify Vertex AI Search datastore is accessible

---

**This should fix the bug in 2 minutes!** 🎯
