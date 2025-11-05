# Add Vertex AI Search Data Store to Dialogflow CX Flow

Since the Generator/Agent Settings doesn't show the data store option, we'll integrate it directly into the conversation flow.

---

## Method 1: Use Playbooks (Recommended if Available)

### Step 1: Check for Playbooks
1. In Dialogflow CX, look for **"Playbooks"** in the left sidebar
2. If you see it, click **"Playbooks"**

### Step 2: Create Playbook
1. Click **"+ Create Playbook"**
2. **Name**: `Clinical Guidelines Lookup`
3. **Description**: `Search clinical guidelines for symptom triage`

### Step 3: Add Data Store
1. In the Playbook configuration
2. Look for **"Data Store"** or **"Knowledge Base"** section
3. Click **"Add Data Store"**
4. Select: `clinical-guidelines-datastore`
5. **Save**

### Step 4: Configure Instructions
Add this instruction text:
```
When the user asks about symptoms, red flags, or triage recommendations:
1. Search the clinical guidelines data store
2. Provide the information with citations
3. Include document ID (e.g., OID-HEADACHE-001) in the response
4. If urgent symptoms, emphasize the need for immediate care
```

### Step 5: Connect to Flow
1. Go to **Build** → **Default Start Flow**
2. Add a route or page that invokes the playbook
3. Test in the console

---

## Method 2: Create Custom Pages with Fallback (Alternative)

If Playbooks aren't available, use this approach:

### Step 1: Enable Agent Fallback
1. Go to **Build** → **Default Start Flow**
2. Click on **"Start"** page
3. Scroll down to **"Event Handlers"**
4. Look for **"No-match default"** or **"Agent fallback"**

### Step 2: Add Generative Fallback
1. In the fallback handler
2. Add fulfillment response
3. Look for option like:
   - **"Generative AI Response"**
   - **"Search Response"**
   - **"Agent Assist"**
4. If you see **"Enable generative AI"** toggle - turn it ON

### Step 3: Configure Generative Response
1. **Model**: `gemini-1.5-flash`
2. **Prompt template**:
```
You are a clinical triage assistant. Answer the user's question based on clinical guidelines.

User question: $request.query-text

Provide:
1. Relevant clinical information
2. Triage recommendation (emergency/urgent/routine/self-care)
3. Citation with document ID

Always cite sources like: [OID-HEADACHE-001, Internal Clinical SOP]
```
3. **Temperature**: `0.2`
4. **Save**

---

## Method 3: Use Search in Agent Builder (Recommended Alternative)

Your datastore is actually in **Vertex AI Agent Builder**, not just Dialogflow CX. Let's use that:

### Step 1: Create Agent Builder App
1. Go to: https://console.cloud.google.com/gen-app-builder/engines?project=ai-agent-health-assistant
2. You should see your datastore: `clinical-guidelines-datastore`
3. Click **"Create App"**
4. Select **"Chat"** (not Search)

### Step 2: Configure Chat App
1. **App name**: `Clinical Guidelines Chat Agent`
2. **Data store**: Select `clinical-guidelines-datastore`
3. **Region**: `Global` or `us-central1`
4. Click **"Create"**

### Step 3: Configure Agent
1. **Company name**: `Your Organization` (or leave as default)
2. **Agent name**: `Clinical Assistant`
3. **Agent description**:
```
A clinical triage assistant that helps evaluate symptoms and provides 
triage recommendations based on clinical guidelines.
```

### Step 4: Configure Agent Instructions
In the **"Agent Instructions"** section, add:
```
You are a clinical triage assistant for a healthcare organization.

Your role:
- Help users understand symptom severity
- Provide triage recommendations (emergency/urgent/routine/self-care)
- Always cite clinical guidelines using document IDs (e.g., OID-HEADACHE-001)

Red flag symptoms require IMMEDIATE escalation to emergency care.

Always be conservative - when in doubt, recommend higher level of care.

Format responses clearly with:
1. Clinical information
2. Triage level and recommendation
3. Citation with [Document ID, Source, Section]
```

### Step 5: Enable Citations
1. In agent settings
2. ✅ Enable **"Show citations"**
3. ✅ Enable **"Grounding"** (if available)
4. **Model**: `gemini-1.5-flash`
5. **Temperature**: `0.2`
6. **Save**

### Step 6: Test the Chat Agent
1. Use the built-in preview (right side of screen)
2. Or click **"Integrations"** → **"Preview"**
3. Test query: `What are red flag headache symptoms?`

### Step 7: Integrate with Dialogflow CX (Optional)
Once the Chat Agent works:
1. Get the Agent Builder API endpoint
2. Create a webhook in Dialogflow CX
3. Call the Agent Builder API from the webhook
4. Return results to Dialogflow

---

## Method 4: Direct API Integration (Advanced)

If all else fails, we can query the datastore directly via webhook:

### Prerequisites
- Cloud Function or Cloud Run service
- Webhook URL configured in Dialogflow CX

### I can help you set this up if needed.

---

## Which Method Should You Try?

**Try this order:**

1. ✅ **Method 3: Agent Builder Chat App** (EASIEST - recommended!)
   - This is designed specifically for this use case
   - Built-in citation support
   - Easy to test and iterate

2. ✅ **Method 1: Playbooks** (if available in your Dialogflow CX)
   - Native integration
   - Good for structured workflows

3. ✅ **Method 2: Generative Fallback** (if no Playbooks)
   - Uses built-in generative AI
   - May not have direct datastore connection

4. ✅ **Method 4: Webhook** (last resort)
   - Full control
   - Requires Cloud Function deployment

---

## Let's Try Method 3 Now

This is actually the **best approach** for your use case:

### Quick Start (5 minutes):

1. **Go to Agent Builder:**
   👉 https://console.cloud.google.com/gen-app-builder/engines?project=ai-agent-health-assistant

2. **Create Chat App** (not Search):
   - Click **"CREATE APP"**
   - Select **"Chat"**
   - Name: `Clinical Guidelines Chat`
   - Data store: `clinical-guidelines-datastore`

3. **Configure Agent** (copy-paste the instructions above)

4. **Test** (should work immediately!)

5. **Optionally integrate** with Dialogflow CX later

---

**This is likely the solution you need!** The Agent Builder Chat is specifically designed for data store + conversational AI.

Would you like me to create a detailed guide for Method 3 (Agent Builder Chat)? This will give you the knowledge-base-powered agent you want! 🚀
