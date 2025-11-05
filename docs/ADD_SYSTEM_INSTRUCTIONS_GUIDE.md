# 📝 How to Add System Instructions in Dialogflow CX Console

## Quick Direct Link

👉 **Direct link to Generative AI Settings:**
https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039/settings/generativeAI

---

## 📋 Step-by-Step Instructions

### **Method 1: Using Dialogflow CX Console (Recommended)**

#### **Step 1: Open Your Agent**
1. Go to: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039
2. You should see your agent: **"Virtual-Health-Assistant-POC"**

#### **Step 2: Navigate to Agent Settings**
1. In the left sidebar, click **"Manage"** (gear icon or "Manage" tab)
2. Click **"Agent Settings"** (or "Settings")

#### **Step 3: Open Generative AI Tab**
1. In the Agent Settings page, you'll see several tabs at the top
2. Click the **"Generative AI"** tab

#### **Step 4: Add System Instructions**
1. Look for a section labeled:
   - **"System Instructions"** or
   - **"Instructions"** or
   - **"System Prompt"** or
   - **"Prompt Template"**

2. If you see a text area or editor, click in it

3. **Copy and paste the following content** (from `system_instructions.txt`):

```
You are a professional, empathetic virtual health assistant helping patients describe their symptoms for triage.

TONE AND STYLE:
- Be warm, professional, and reassuring
- Use clear, simple language
- Show empathy and understanding
- Be concise but thorough

FEW-SHOT EXAMPLES:

Example 1 - Low Urgency Headache:
User: "I have a headache"
Assistant: "I understand you're experiencing a headache. To help determine the best next steps, can you tell me when this started?"
User: "It started this morning"
Assistant: "Thank you. On a scale of 0 to 10, how would you rate the severity of your headache?"
User: "About a 3"
Assistant: "Based on your symptoms—a mild headache that started this morning—this may improve with rest and self-care. If symptoms persist beyond 3 days or worsen, please schedule a follow-up."

Example 2 - High Urgency Red Flag:
User: "I have a really bad headache and my vision is blurry"
Assistant: "Thank you for letting me know. Headache with vision changes can be a sign of a serious condition. I recommend seeking immediate medical attention. Please call your healthcare provider's emergency line or go to the nearest emergency department."

Example 3 - Medium Urgency Nausea:
User: "Feeling nauseous since last night, can't keep food down"
Assistant: "I understand you're experiencing nausea and vomiting. This warrants medical evaluation. I recommend scheduling a same-week appointment with your primary care provider or using our telehealth service."

CLASSIFICATION GUIDELINES:
- HIGH urgency: Severe symptoms (8+/10), red flags (vision changes, chest pain, neurological symptoms), or life-threatening symptoms
- MEDIUM urgency: Moderate symptoms (5-7/10), persistent symptoms (>3 days), or inability to keep fluids down
- LOW urgency: Mild symptoms (<5/10), short duration, no red flags

IMPORTANT:
- Always be empathetic and reassuring
- Provide clear next steps
- For red flags, emphasize urgency without causing panic
- Include medical disclaimers when appropriate
- Never provide definitive diagnoses, only triage recommendations
```

4. Click **"SAVE"** or **"Save"** button (usually at the top or bottom of the page)

---

### **Method 2: Using Vertex AI Agent Builder UI (Alternative)**

#### **Step 1: Open Agent Builder**
1. Go to: https://console.cloud.google.com/vertex-ai/agent-builder
2. Select your project: **ai-agent-health-assistant**
3. Find and click on your agent: **"Virtual-Health-Assistant-POC"**

#### **Step 2: Navigate to Settings**
1. Click **"Settings"** in the left sidebar or top navigation
2. Look for **"System Instructions"** or **"Instructions"** section

#### **Step 3: Add Instructions**
1. Paste the same content from above
2. Click **"Save"**

---

## 🔍 What to Look For

### **If you don't see "System Instructions" field:**

1. **Check the Generative AI Model Settings:**
   - Make sure you have a Generative AI model enabled (Gemini 1.5 Flash, Gemini Pro, etc.)
   - System Instructions are typically available when Generative AI is enabled

2. **Look for these alternative names:**
   - "Instructions"
   - "System Prompt"
   - "Prompt Template"
   - "Agent Instructions"
   - "Base Instructions"

3. **Check the Flow Settings:**
   - Sometimes system instructions are at the Flow level
   - Go to your "Default Start Flow"
   - Check Flow settings → Generative AI settings

---

## ✅ Verification

After adding system instructions:

1. **Test the agent** in the Console:
   - Click the **"Test Agent"** button (usually in the top right)
   - Try a query like: "I have a headache"
   - The response should reflect the tone and style from the instructions

2. **Check the response:**
   - Should be warm and empathetic
   - Should ask clarifying questions
   - Should follow the classification guidelines

---

## 📎 Quick Copy-Paste Content

The full content is saved in: **`system_instructions.txt`**

You can also copy it directly from the code block above.

---

## 🆘 Troubleshooting

### **Issue: "System Instructions" field not visible**
- **Solution:** Make sure Generative AI is enabled for your agent
- Go to: Agent Settings → Generative AI → Enable "Use Generative AI"

### **Issue: Can't find the Settings page**
- **Solution:** Use the direct link provided at the top
- Or navigate: Manage → Agent Settings → Generative AI tab

### **Issue: Changes not reflecting**
- **Solution:** 
  1. Make sure you clicked "Save"
  2. Wait a few seconds for changes to propagate
  3. Try testing with a new session
  4. Clear browser cache if needed

---

## 📞 Need Help?

If you still can't find the System Instructions field:
1. Check that your agent has Generative AI enabled
2. Verify you're in the correct project and region (us-central1)
3. Try refreshing the page
4. Check the Dialogflow CX documentation for your specific UI version

---

**Last Updated:** November 4, 2025  
**Agent ID:** 72d18125-ac71-4c56-8ea0-44bfc7f9b039  
**Project:** ai-agent-health-assistant  
**Location:** us-central1

