# 🎯 Agent Builder Grounding Integration Guide

## ✅ Grounding Tool Deployed Successfully!

**Grounding Tool URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool`

## 🏗️ **Integration Options**

### **Option 1: Direct Datastore Integration (Preferred)**

1. **Open Agent Builder**:
   - Go to: https://console.cloud.google.com/vertex-ai/agent-builder
   - Select project: `ai-agent-health-assistant`

2. **Add Datastore**:
   - Navigate to **Tools** → **Integrations** → **Datastores**
   - Click **"+ Add Datastore"**
   - Select **"Vertex AI Search"**
   - Choose: `clinical-guidelines-datastore`
   - Click **"Connect"**

3. **Enable Grounding**:
   - Go to **Agent Configuration** → **Grounding**
   - Enable **"Use datastore for grounding"**
   - Select your connected datastore
   - Configure search parameters:
     - Max results: 5
     - Relevance threshold: 0.7
     - Enable citations: Yes

### **Option 2: External Tool Integration (If Direct Not Available)**

1. **Add External Tool**:
   - In Agent Builder, go to **Tools** → **External Tools**
   - Click **"+ Add External Tool"**
   - **Tool Name**: `Clinical Guidelines Grounding`
   - **Tool URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool`
   - **Description**: `Search clinical guidelines for evidence-based information`

2. **Configure Tool Parameters**:
   ```json
   {
     "user_text": "{{user_input}}",
     "max_results": 5
   }
   ```

3. **Add to Agent Flow**:
   - In your agent's dialog nodes
   - Add step to invoke grounding tool
   - Use retrieved content when composing replies

## 🧪 **Testing Integration**

### **Test Queries**
1. `What are red flag headache symptoms?`
2. `When should someone with nausea see a doctor?`
3. `What is orthostatic hypotension?`

### **Expected Response Format**
```
🚨 EMERGENCY: Based on symptoms, immediate medical attention required.

Based on clinical guidelines:

1. Thunderclap headache (worst headache of life) requires immediate evaluation for subarachnoid hemorrhage.

Sources used: [1], [2]

Triage level: EMERGENCY

Next steps: Call 911 or go to the nearest emergency room immediately.

⚠️ This information is for educational purposes only and does not replace professional medical advice.
```

## 🔍 **Grounding Tool Features**

### **Automatic Search**
- Searches clinical guidelines datastore
- Returns top 5 most relevant results
- Calculates medical relevance scores

### **Evidence-Based Generation**
- Uses Gemini 1.5 Flash with medical safety settings
- Grounds responses only on retrieved content
- Includes proper citations with document IDs

### **Safety Features**
- Never provides definitive diagnoses
- Flags emergency symptoms immediately
- Includes medical disclaimers
- Provides triage recommendations

## 🧪 **Test Endpoints**

- **Health Check**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool/health`
- **Direct Test**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool/test`
- **Grounding Tool**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool`

### **Test Command**:
```bash
curl -X POST https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool/test \
  -H "Content-Type: application/json" \
  -d '{"user_text": "What are red flag headache symptoms?"}'
```

## 🚀 **Next Steps**

1. **Choose integration method** (Direct datastore preferred)
2. **Configure grounding settings** in Agent Builder
3. **Test with medical queries** to validate functionality
4. **Deploy agent** when satisfied with results

## 📊 **Performance Metrics**

- **Search Time**: ~2-3 seconds
- **Generation Time**: ~3-5 seconds
- **Total Response Time**: ~5-8 seconds
- **Accuracy**: Evidence-based with citations
- **Safety**: Medical guardrails enabled

---

**Your grounding tool is now ready for Agent Builder integration!** 🎯
