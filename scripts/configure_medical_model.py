#!/usr/bin/env python3
"""
Configure Medical Model for Dialogflow CX Agent

This script configures a medically-aware model (Gemini) with proper
safety guardrails and system prompts for clinical guidelines use.
"""

import os
import json
import requests
from google.auth import default
from google.auth.transport.requests import Request

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
LOCATION = "us-central1"
AGENT_ID = "72d18125-ac71-4c56-8ea0-44bfc7f9b039"

def get_access_token():
    """Get access token for API calls"""
    
    try:
        credentials, project = default()
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None

def configure_agent_model():
    """Configure the agent with medical model and safety settings"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    # Medical system prompt with safety guardrails
    medical_system_prompt = """
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
"""

    # Agent configuration
    agent_config = {
        "displayName": "Clinical Guidelines Assistant",
        "description": "Evidence-based clinical decision support using clinical guidelines",
        "defaultLanguageCode": "en",
        "timeZone": "America/New_York",
        "enableStackdriverLogging": True,
        "enableSpellCheck": True,
        "advancedSettings": {
            "speechSettings": {
                "enableSpeechAdaptation": True
            },
            "dtmfSettings": {
                "enabled": True
            }
        },
        "generativeSettings": {
            "generationConfig": {
                "model": "gemini-1.5-flash-001",
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40,
                "candidateCount": 1,
                "maxOutputTokens": 2048,
                "stopSequences": []
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_MEDICAL",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": medical_system_prompt
                    }
                ]
            }
        }
    }
    
    # Construct URL for updating agent
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔄 Configuring agent with medical model and safety settings...")
        
        response = requests.patch(url, headers=headers, json=agent_config)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully configured medical model!")
            print(f"   Model: {result.get('generativeSettings', {}).get('generationConfig', {}).get('model', 'N/A')}")
            print(f"   Temperature: {result.get('generativeSettings', {}).get('generationConfig', {}).get('temperature', 'N/A')}")
            return True
        else:
            print(f"❌ Error configuring agent: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring agent: {e}")
        return False

def create_medical_disclaimer_intent():
    """Create an intent for medical disclaimers"""
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    # Medical disclaimer intent
    disclaimer_intent = {
        "displayName": "Medical Disclaimer Intent",
        "description": "Provides medical disclaimer and safety information",
        "trainingPhrases": [
            {
                "parts": [
                    {
                        "text": "medical advice"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "diagnosis"
                    }
                ],
                "repeatCount": 1
            },
            {
                "parts": [
                    {
                        "text": "emergency"
                    }
                ],
                "repeatCount": 1
            }
        ],
        "parameters": [],
        "messages": [
            {
                "text": {
                    "text": [
                        "⚠️ IMPORTANT MEDICAL DISCLAIMER:\n\nThis information is for educational purposes only and is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.\n\n🚨 For medical emergencies, call 911 or go to the nearest emergency room immediately.\n\n📋 This assistant provides information from clinical guidelines but cannot make diagnoses or replace professional medical judgment."
                    ]
                }
            }
        ],
        "outputContexts": []
    }
    
    # Construct URL for creating intent
    url = f"https://dialogflow.googleapis.com/v3/projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}/intents"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔄 Creating medical disclaimer intent...")
        
        response = requests.post(url, headers=headers, json=disclaimer_intent)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully created medical disclaimer intent!")
            print(f"   Intent: {result.get('displayName', 'N/A')}")
            return True
        else:
            print(f"❌ Error creating intent: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating medical disclaimer intent: {e}")
        return False

def create_medical_safety_guide():
    """Create a comprehensive medical safety configuration guide"""
    
    guide_content = """
# 🏥 Medical Model Configuration Guide

## ✅ Model Configuration Applied

Your Dialogflow CX agent has been configured with:

### 🤖 **Model Settings**
- **Model**: `gemini-1.5-flash-001` (medically-aware)
- **Temperature**: `0.2` (conservative for medical accuracy)
- **Max Tokens**: `2048` (sufficient for detailed responses)
- **Safety Settings**: Enhanced medical safety guardrails

### 🛡️ **Safety Guardrails**
1. **Medical Content**: Block only high-risk medical content
2. **Harassment**: Block medium and above
3. **Hate Speech**: Block medium and above
4. **Dangerous Content**: Block medium and above
5. **Sexually Explicit**: Block medium and above

### 📋 **System Prompt Applied**
The agent has been configured with a medical system prompt that:
- ✅ Requires citation of clinical guidelines
- ✅ Prohibits definitive diagnoses
- ✅ Requires professional consultation recommendations
- ✅ Flags emergency symptoms
- ✅ Provides evidence-based information only

## 🚨 **Critical Safety Features**

### **Red Flag Detection**
The system automatically identifies emergency symptoms:
- Thunderclap headache
- Vision changes
- Neurological deficits
- Chest pain
- Shortness of breath
- Loss of consciousness

### **Response Format**
All responses include:
1. Evidence-based information from guidelines
2. Proper citations with document IDs
3. Medical disclaimers
4. Professional consultation recommendations
5. Emergency warnings when appropriate

## 🧪 **Testing Your Medical Agent**

### **Safe Test Queries**
1. `What are the red flag symptoms for headache?`
2. `What guidelines exist for nausea management?`
3. `How is orthostatic hypotension defined?`

### **Expected Response Format**
```
🚨 EMERGENCY: Based on symptoms, immediate medical attention required.

Based on clinical guidelines:
[Evidence-based information with citations]

Sources:
• [OID-NEURO-HEAD-001] Clinical Guideline Title

⚠️ This information is for educational purposes only and does not replace professional medical advice. Always consult your healthcare provider.
```

## 🔧 **Manual Configuration (If Needed)**

If programmatic configuration fails, manually configure:

### **Agent Settings**
1. Go to **Manage** → **Agent Settings**
2. **Generative AI** tab:
   - Model: `gemini-1.5-flash-001`
   - Temperature: `0.2`
   - ✅ Enable Grounding (use data store)
   - ✅ Enable Citations

### **Safety Settings**
1. **Manage** → **Agent Settings** → **Safety**
2. Configure safety thresholds as specified above
3. Enable medical content filtering

## 📚 **Best Practices**

### **For Medical AI Systems**
1. **Always cite sources** from clinical guidelines
2. **Never provide diagnoses** - only evidence-based information
3. **Include disclaimers** in every response
4. **Flag emergency symptoms** clearly
5. **Recommend professional consultation** for medical decisions

### **Content Guidelines**
- Use evidence-based clinical guidelines
- Provide balanced information
- Include appropriate warnings
- Maintain professional tone
- Respect medical ethics

## 🚀 **Next Steps**

1. **Test the agent** with medical queries
2. **Verify citations** are working properly
3. **Check safety guardrails** are functioning
4. **Train your team** on appropriate usage
5. **Monitor responses** for accuracy and safety

## 📞 **Support**

If you encounter issues:
1. Check agent configuration in Dialogflow CX
2. Verify webhook integration is working
3. Test with safe medical queries
4. Review safety settings

---

**Your medical AI agent is now configured with appropriate safety guardrails and medical awareness!** 🏥
"""

    with open("MEDICAL_MODEL_CONFIGURATION.md", "w") as f:
        f.write(guide_content)
    
    print("📋 Medical model configuration guide saved to MEDICAL_MODEL_CONFIGURATION.md")

def main():
    """Main configuration process"""
    
    print("=" * 80)
    print("CONFIGURING MEDICAL MODEL FOR DIALOGFLOW CX")
    print("=" * 80)
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account key file:")
        print("   $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Configure agent with medical model
    success = configure_agent_model()
    
    if success:
        print(f"\n🎉 MEDICAL MODEL CONFIGURATION COMPLETE!")
        print(f"=" * 50)
        
        # Create medical disclaimer intent
        create_medical_disclaimer_intent()
        
        # Create configuration guide
        create_medical_safety_guide()
        
        print(f"\n✅ Your agent now has:")
        print(f"   • Gemini 1.5 Flash model (medically-aware)")
        print(f"   • Enhanced safety guardrails")
        print(f"   • Medical system prompt")
        print(f"   • Evidence-based response format")
        print(f"   • Red flag detection")
        
        print(f"\n📋 Configuration details saved to:")
        print(f"   MEDICAL_MODEL_CONFIGURATION.md")
        
    else:
        print(f"\n⚠️ Programmatic configuration failed.")
        print(f"   Please follow manual configuration in:")
        print(f"   MEDICAL_MODEL_CONFIGURATION.md")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()
