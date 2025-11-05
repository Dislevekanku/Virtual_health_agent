# 🐛 Fix Webhook Integration Bug

## **Problem Identified**
Your agent responds with "Sorry, can you say that again?" instead of calling the RAG webhook for medical queries.

## **Root Cause**
The webhook exists but isn't connected to the flow's fulfillment logic.

## 🔧 **Fix Options**

### **Option 1: Add Webhook to Default Start Flow (Recommended)**

1. **Go to Build Tab** (left sidebar)
2. **Click on "Default Start Flow"**
3. **Click on "Start Page"**
4. **Scroll down to find "Entry fulfillment" section**
5. **Add webhook**:
   - Click **"+ Add fulfillment"** or **"+ Add dialogue option"**
   - Select **"Call webhook"**
   - Choose: `clinical-guidelines-webhook`
   - Click **"Save"**

### **Option 2: Create Medical Intent (Alternative)**

1. **Go to Build Tab**
2. **Click on "Intents"**
3. **Click "+ Create Intent"**
4. **Intent Name**: `Medical Query Intent`
5. **Training Phrases**:
   ```
   What are red flag headache symptoms?
   When should I see a doctor for nausea?
   What is orthostatic hypotension?
   Tell me about dizziness guidelines
   Medical advice
   Clinical guidelines
   Health symptoms
   ```
6. **Fulfillment**:
   - Enable **"Enable webhook call for this intent"**
   - Webhook: `clinical-guidelines-webhook`
7. **Click "Save"**

### **Option 3: Update Default Welcome Intent**

1. **Go to Build Tab**
2. **Click on "Intents"**
3. **Click on "Default Welcome Intent"**
4. **Fulfillment**:
   - Enable **"Enable webhook call for this intent"**
   - Webhook: `clinical-guidelines-webhook`
5. **Click "Save"**

## 🧪 **Test After Fix**

1. **Go to Preview panel** (right side)
2. **Type**: `What are red flag headache symptoms?`
3. **Expected**: Should call your RAG webhook and return clinical guidelines with citations

## 🔍 **Verify Webhook is Working**

Test your webhook directly:
```bash
curl -X POST https://us-central1-ai-agent-health-assistant.cloudfunctions.net/simplified-rag-webhook/test \
  -H "Content-Type: application/json" \
  -d '{"query": "What are red flag headache symptoms?"}'
```

Expected response should include:
- Clinical guidelines information
- Citations like [OID-NEURO-HEAD-001]
- Triage level (Emergency/Urgent/Routine)
- Medical disclaimer

## 🚨 **Common Issues & Solutions**

### **Issue 1: "No matching intent"**
- **Solution**: Add training phrases to your intent or create a catch-all intent

### **Issue 2: Webhook not called**
- **Solution**: Ensure webhook is enabled in fulfillment settings

### **Issue 3: Webhook timeout**
- **Solution**: Check Cloud Function logs for errors

### **Issue 4: "Sorry, can you say that again?"**
- **Solution**: This means no intent matched - add more training phrases or fix fulfillment

## 📋 **Quick Checklist**

- ✅ Webhook exists in Manage → Webhooks
- ✅ Webhook URL is correct
- ⚠️ Webhook connected to flow/intent fulfillment
- ⚠️ Intent has appropriate training phrases
- ⚠️ Fulfillment enabled for webhook

## 🎯 **Recommended Fix**

**Use Option 1** - Add webhook to Default Start Flow Entry fulfillment. This will make the webhook trigger for any user input that doesn't match other intents.

---

**After implementing the fix, test with: "What are red flag headache symptoms?"**
