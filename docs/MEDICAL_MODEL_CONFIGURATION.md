# 🏥 Medical Model Configuration Guide

## 🎯 **Recommended Medical Model: Gemini 1.5 Flash**

**Why Gemini 1.5 Flash?**
- ✅ Medically-aware and trained on medical literature
- ✅ Better than deprecated MedLM
- ✅ Available in Vertex AI Model Garden
- ✅ Supports grounding and citations
- ✅ Configurable safety settings

## 🔧 **Manual Configuration Steps**

### **Step 1: Configure Agent Settings**

1. **Go to Dialogflow CX Agent**:
   - URL: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

2. **Navigate to Agent Settings**:
   - Click **"Manage"** tab (left sidebar)
   - Click **"Agent Settings"**
   - Click **"Generative AI"** tab

3. **Configure Model Settings**:
   ```
   Model: gemini-1.5-flash-001
   Temperature: 0.2 (conservative for medical accuracy)
   Max Output Tokens: 2048
   ```

4. **Enable Grounding and Citations**:
   - ✅ **Enable Grounding** (use data store)
   - ✅ **Enable Citations** (show sources)

### **Step 2: Configure Safety Settings**

1. **In Agent Settings, go to "Safety" tab**

2. **Set Safety Thresholds**:
   ```
   Medical Content: Block Only High
   Harassment: Block Medium and Above
   Hate Speech: Block Medium and Above
   Dangerous Content: Block Medium and Above
   Sexually Explicit: Block Medium and Above
   ```

### **Step 3: Configure System Prompt**

1. **In Agent Settings, go to "Generative AI" tab**

2. **Add System Instruction**:
   ```
   You are a clinical decision support assistant that provides evidence-based information from clinical guidelines. 

   CRITICAL SAFETY RULES:
   1. NEVER provide definitive diagnoses
   2. NEVER replace professional medical judgment
   3. ALWAYS cite sources from retrieved clinical guidelines
   4. ALWAYS recommend consulting healthcare providers for medical decisions
   5. Flag emergency symptoms requiring immediate attention

   RESPONSE FORMAT:
   - Use retrieved clinical guidelines as primary source
   - Provide evidence-based information with citations
   - Include appropriate disclaimers
   - Flag red flag symptoms clearly

   When users ask medical questions:
   1. Search clinical guidelines database
   2. Provide evidence-based information with citations
   3. Include appropriate medical disclaimers
   4. Recommend professional consultation when appropriate
   ```

### **Step 4: Configure Webhook Integration**

1. **Ensure your webhook is configured** (from previous steps):
   - Webhook URL: `https://us-central1-ai-agent-health-assistant.cloudfunctions.net/clinical-guidelines-webhook/webhook`
   - Webhook name: `clinical-guidelines-webhook`

2. **In your flow's Start Page**:
   - Add webhook to Entry fulfillment
   - This enables grounding with your clinical guidelines datastore

## 🛡️ **Safety Guardrails Configuration**

### **Medical Content Filtering**
- **Block Level**: Only High (allows medical education content)
- **Purpose**: Prevent dangerous medical advice while allowing educational content

### **Response Validation**
The system will automatically:
- ✅ Require citations from clinical guidelines
- ✅ Flag emergency symptoms
- ✅ Include medical disclaimers
- ✅ Recommend professional consultation

### **Red Flag Detection**
Automatically identifies emergency symptoms:
- 🚨 Thunderclap headache
- 🚨 Vision changes
- 🚨 Neurological deficits
- 🚨 Chest pain
- 🚨 Shortness of breath
- 🚨 Loss of consciousness

## 📋 **Expected Response Format**

### **Safe Medical Query Response**
```
🚨 EMERGENCY: Based on symptoms described, immediate medical attention is required.

Based on clinical guidelines:

1. Thunderclap headache (worst headache of life) requires immediate evaluation for subarachnoid hemorrhage.

2. Visual changes with headache may indicate increased intracranial pressure.

Sources:
• [OID-NEURO-HEAD-001] OID-Headache-Guideline
• [OID-NEURO-HEAD-002] Red Flag Symptoms Protocol

⚠️ This information is for educational purposes only and does not replace professional medical advice. Always consult your healthcare provider for medical decisions.
```

### **Triage Recommendations**
- 🚨 **Emergency**: Immediate medical attention required
- ⚡ **Urgent**: Same-day evaluation needed  
- 📋 **Routine**: Standard care appropriate

## 🧪 **Testing Your Medical Agent**

### **Safe Test Queries**
1. `What are red flag headache symptoms?`
2. `When should someone with nausea see a doctor?`
3. `What is orthostatic hypotension?`
4. `What guidelines cover dizziness and vertigo?`

### **Expected Behavior**
- ✅ Returns evidence-based information
- ✅ Includes proper citations
- ✅ Flags emergency symptoms
- ✅ Includes medical disclaimers
- ✅ Recommends professional consultation

## 🚨 **Critical Safety Features**

### **Never Do**
- ❌ Provide definitive diagnoses
- ❌ Replace professional medical judgment
- ❌ Give treatment recommendations
- ❌ Ignore emergency symptoms

### **Always Do**
- ✅ Cite clinical guidelines
- ✅ Include medical disclaimers
- ✅ Flag emergency symptoms
- ✅ Recommend professional consultation
- ✅ Provide evidence-based information

## 📚 **Best Practices**

### **For Medical AI Systems**
1. **Evidence-Based**: Only use information from clinical guidelines
2. **Transparent**: Always cite sources
3. **Safe**: Include appropriate warnings and disclaimers
4. **Professional**: Maintain medical ethics standards
5. **Educational**: Focus on information, not diagnosis

### **Content Guidelines**
- Use peer-reviewed clinical guidelines
- Provide balanced information
- Include appropriate warnings
- Maintain professional medical tone
- Respect patient privacy and dignity

## 🔍 **Alternative Models (If Gemini Not Available)**

### **Vertex AI Model Garden Options**
1. **Gemini Pro**: General purpose, good for medical content
2. **PaLM 2**: Alternative with medical capabilities
3. **Custom Medical Models**: If you have access to specialized medical models

### **Configuration for Alternatives**
- Temperature: 0.1-0.3 (conservative)
- Max tokens: 2048-4096
- Safety settings: Block high-risk medical content
- System prompts: Medical-focused instructions

## 🚀 **Next Steps**

1. **Configure the model** using the steps above
2. **Test with medical queries** to verify safety
3. **Train your team** on appropriate usage
4. **Monitor responses** for accuracy and safety
5. **Regularly update** clinical guidelines

## 📞 **Support and Validation**

### **Validation Checklist**
- ✅ Model configured (Gemini 1.5 Flash)
- ✅ Safety settings enabled
- ✅ System prompt configured
- ✅ Webhook integrated
- ✅ Citations enabled
- ✅ Grounding enabled

### **Testing Protocol**
1. Test with safe medical queries
2. Verify citations are working
3. Check emergency symptom detection
4. Validate disclaimer inclusion
5. Confirm professional consultation recommendations

---

## 🎉 **Success!**

Your medical AI agent is now configured with:
- ✅ Medically-aware Gemini model
- ✅ Enhanced safety guardrails  
- ✅ Evidence-based response format
- ✅ Red flag detection
- ✅ Proper medical disclaimers
- ✅ Clinical guidelines integration

**Your agent is ready for safe medical decision support!** 🏥
