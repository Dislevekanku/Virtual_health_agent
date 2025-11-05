# 🎯 Complete Agent Builder Setup Guide

## ✅ **Your Grounding Tool is Ready!**

**Grounding Tool URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool`

## 🚀 **Quick Setup (10-30 minutes)**

### **Step 1: Open Agent Builder**
1. **Go to**: https://console.cloud.google.com/vertex-ai/agent-builder
2. **Select project**: `ai-agent-health-assistant`
3. **Click**: **"+ Create Agent"** or use existing agent

### **Step 2: Configure Agent Settings**

#### **Basic Configuration**
- **Agent Name**: `Clinical Guidelines Assistant`
- **Description**: `Clinical decision support agent with grounding capabilities`
- **Default Language**: `English`
- **Time Zone**: `America/New_York`

#### **Model Configuration**
- **Model**: `gemini-1.5-flash-001`
- **Temperature**: `0.2`
- **Max Output Tokens**: `2048`

#### **Safety Settings**
- **Medical Content**: `Block Only High`
- **Harassment**: `Block Medium and Above`
- **Dangerous Content**: `Block Medium and Above`

### **Step 3: Add System Instructions**

```
You are a clinical decision support assistant that provides evidence-based information from clinical guidelines.

CRITICAL SAFETY RULES:
1. NEVER provide definitive diagnoses
2. NEVER replace professional medical judgment
3. ALWAYS cite sources from retrieved clinical guidelines
4. ALWAYS recommend consulting healthcare providers for medical decisions
5. Flag emergency symptoms requiring immediate attention

When users ask medical questions:
1. Search clinical guidelines database
2. Provide evidence-based information with citations
3. Include appropriate medical disclaimers
4. Recommend professional consultation when appropriate
```

### **Step 4: Integration Options**

#### **Option A: Direct Datastore Integration (Preferred)**

1. **Navigate to**: Tools → Integrations → Datastores
2. **Click**: "+ Add Datastore"
3. **Select**: "Vertex AI Search"
4. **Choose**: `clinical-guidelines-datastore`
5. **Click**: "Connect"

**Configure Grounding Settings**:
- **Enable Grounding**: ✅
- **Max Results**: `5`
- **Relevance Threshold**: `0.7`
- **Enable Citations**: ✅
- **Search Mode**: `Hybrid`

#### **Option B: External Tool Integration**

1. **Navigate to**: Tools → External Tools
2. **Click**: "+ Add External Tool"
3. **Configure**:
   - **Tool Name**: `Clinical Guidelines Grounding`
   - **Tool URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool`
   - **Description**: `Search clinical guidelines for evidence-based information`

4. **Tool Parameters**:
   ```json
   {
     "user_text": "{{user_input}}",
     "max_results": 5
   }
   ```

5. **Add to Flow**: Configure dialog nodes to call this tool

### **Step 5: Create Medical Intents**

#### **Intent 1: Medical Query Intent**
- **Name**: `Medical Query Intent`
- **Training Phrases**:
  ```
  What are red flag headache symptoms?
  When should I see a doctor for nausea?
  What is orthostatic hypotension?
  Tell me about dizziness guidelines
  Medical advice
  Health symptoms
  Clinical guidelines
  ```

- **Fulfillment**: 
  - **Enable webhook call**: ✅
  - **Webhook URL**: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/grounding-tool`

#### **Intent 2: Emergency Symptoms Intent**
- **Name**: `Emergency Symptoms Intent`
- **Training Phrases**:
  ```
  I have chest pain
  Worst headache of my life
  Vision changes
  Difficulty breathing
  Loss of consciousness
  Severe abdominal pain
  ```

- **Fulfillment**:
  - **Response**: `🚨 EMERGENCY: Based on your symptoms, please call 911 or go to the nearest emergency room immediately.`
  - **Enable webhook call**: ✅

### **Step 6: Configure Flow**

#### **Default Start Flow**
1. **Open**: Default Start Flow
2. **Start Page Configuration**:
   - **Entry Fulfillment**: Enable grounding tool call
   - **Routes**: Add medical intent routing

#### **Route Configuration**
- **Route 1**: Medical Query Intent → Call Grounding Tool
- **Route 2**: Emergency Symptoms Intent → Emergency Response
- **Default Route**: General medical guidance

### **Step 7: Test Integration**

#### **Test Queries**
1. `What are red flag headache symptoms?`
2. `When should someone with nausea see a doctor?`
3. `What is orthostatic hypotension?`
4. `I have chest pain` (Emergency test)

#### **Expected Responses**
```
🚨 EMERGENCY: Based on symptoms, immediate medical attention required.

Based on clinical guidelines:

1. Thunderclap headache (worst headache of life) requires immediate evaluation for subarachnoid hemorrhage.

Sources used: [1], [2]

Triage level: EMERGENCY

Next steps: Call 911 or go to the nearest emergency room immediately.

⚠️ This information is for educational purposes only and does not replace professional medical advice.
```

## 🧪 **Validation Checklist**

### **✅ Agent Configuration**
- [ ] Model: `gemini-1.5-flash-001`
- [ ] Temperature: `0.2`
- [ ] Safety settings configured
- [ ] System instructions added

### **✅ Grounding Integration**
- [ ] Datastore connected OR external tool configured
- [ ] Grounding enabled
- [ ] Citations enabled
- [ ] Max results: 5

### **✅ Intent Configuration**
- [ ] Medical Query Intent created
- [ ] Emergency Symptoms Intent created
- [ ] Webhook fulfillment configured
- [ ] Training phrases added

### **✅ Flow Configuration**
- [ ] Routes configured
- [ ] Default responses set
- [ ] Emergency routing working

### **✅ Testing**
- [ ] Medical queries return guidelines
- [ ] Citations appear in responses
- [ ] Emergency symptoms trigger warnings
- [ ] Medical disclaimers included

## 🚨 **Troubleshooting**

### **No Grounding Results**
- Check datastore connection
- Verify grounding settings
- Test external tool directly
- Check agent permissions

### **No Citations**
- Enable citations in grounding settings
- Verify datastore has document IDs
- Check response formatting

### **Emergency Detection Not Working**
- Verify emergency intent training phrases
- Check route configuration
- Test emergency keywords

### **Webhook Not Called**
- Verify webhook URL
- Check intent fulfillment settings
- Test webhook directly

## 📊 **Performance Metrics**

- **Response Time**: 5-8 seconds (search + generation)
- **Accuracy**: Evidence-based with citations
- **Safety**: Medical guardrails enabled
- **Coverage**: Clinical guidelines datastore

## 🎯 **Success Criteria**

Your agent is working correctly when:
- ✅ Medical queries return clinical guidelines
- ✅ Responses include proper citations
- ✅ Emergency symptoms are flagged
- ✅ Medical disclaimers are included
- ✅ Triage recommendations are provided

## 🔗 **Access Your Agent**

Once configured, access your agent at:
`https://console.cloud.google.com/vertex-ai/agent-builder/projects/ai-agent-health-assistant/locations/us-central1/agents/{AGENT_ID}`

---

## 🎉 **You're Ready!**

Your Agent Builder integration is complete with:
- ✅ Clinical guidelines grounding
- ✅ Evidence-based responses
- ✅ Emergency detection
- ✅ Medical safety guardrails
- ✅ Citation support

**Total setup time: 10-30 minutes as requested!** 🚀
