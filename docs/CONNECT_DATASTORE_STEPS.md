# Connect Datastore to Dialogflow CX Agent - Step by Step

## 🤖 Quick Configuration (5 minutes)

Follow these exact steps to connect your datastore to the agent.

---

## Step 1: Open Agent Settings

**Click this direct link:**
👉 https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039/settings/generativeAI

Or navigate manually:
1. Go to: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039
2. Click **"Manage"** in left sidebar
3. Click **"Agent Settings"**
4. Click **"Generative AI"** tab

---

## Step 2: Add Data Store

### 2.1 Connect Datastore
1. Scroll to **"Data stores"** section
2. Click **"+ ADD DATA STORE"** button
3. You'll see a list of available datastores
4. Select: **`clinical-guidelines-datastore`**
5. Click **"SAVE"**

### 2.2 Verify Connection
- You should now see `clinical-guidelines-datastore` listed
- Status should show as "Active" or "Connected"

---

## Step 3: Configure Generative AI Model

### 3.1 Model Selection
1. In the same "Generative AI" tab
2. Under **"Generators"** or **"Model"** section
3. Click **"Edit"** or configure model settings
4. Select model: **`gemini-1.5-flash`**
   - Alternative: `gemini-1.5-pro` (more accurate but slower/costlier)
   - Alternative: `gemini-pro` (if flash not available)

### 3.2 Model Parameters
Set these values:
- **Temperature**: `0.2` (low for clinical accuracy)
  - Range: 0.0 (deterministic) to 1.0 (creative)
  - Clinical use needs consistency, so keep low
- **Max output tokens**: `1024` (default is fine)
- **Top K**: `40` (default is fine)
- **Top P**: `0.95` (default is fine)

---

## Step 4: Enable Key Features

### 4.1 Grounding
✅ **Enable "Grounding"** or **"Use data store for grounding"**
- This ensures responses are based on your guidelines
- Reduces hallucination
- Critical for clinical accuracy

### 4.2 Citations
✅ **Enable "Citations"** or **"Show citations"**
- Displays source documents in responses
- Shows document ID and section
- Essential for transparency and trust

### 4.3 Safety Settings (Optional)
- Keep default safety settings
- Blocks harmful or inappropriate content
- Can adjust if needed for your use case

---

## Step 5: Save Configuration

1. Review all settings:
   - ✓ Datastore: `clinical-guidelines-datastore` connected
   - ✓ Model: `gemini-1.5-flash` selected
   - ✓ Temperature: `0.2` set
   - ✓ Grounding: Enabled
   - ✓ Citations: Enabled

2. Click **"SAVE"** button at bottom of page

3. Wait for confirmation message: "Settings saved successfully"

---

## Step 6: Test Your Agent

### 6.1 Open Test Console
1. Click **"Test Agent"** button (top right corner)
2. Or go to: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039/test

### 6.2 Test Query 1: Red Flags
**Type this in the test console:**
```
What are red flag headache symptoms?
```

**Expected Response:**
- Should mention: thunderclap headache, vision changes, neurological deficits, fever + neck stiffness
- Should cite: **OID-HEADACHE-001** or **Headache Evaluation Guideline**
- Should include source attribution: "Internal Clinical SOP" or similar
- Citation format might be: `[1]` or `(Source: OID-HEADACHE-001)`

### 6.3 Test Query 2: Triage
**Type this:**
```
I've been vomiting for 2 days and can't keep water down
```

**Expected Response:**
- Should recognize urgent evaluation needed
- Should mention: persistent vomiting >24 hours requires same-day care
- Should cite: **OID-GI-NAUSEA-002** or **Nausea and Vomiting Guideline**
- May recommend: hydration assessment, IV fluids, antiemetics

### 6.4 Test Query 3: Specific Condition
**Type this:**
```
What is orthostatic hypotension?
```

**Expected Response:**
- Should define: Blood pressure drop ≥20/10 mmHg within 3 minutes of standing
- Should explain symptoms: dizziness, lightheadedness when standing
- Should cite: **OID-CARDIO-ORTHO-005** or **Orthostatic Hypotension Guideline**
- May include assessment and management info

---

## ✅ Success Checklist

Verify all of these before marking complete:

- [ ] Datastore `clinical-guidelines-datastore` is connected
- [ ] Model `gemini-1.5-flash` is selected
- [ ] Temperature is set to `0.2`
- [ ] Grounding is enabled
- [ ] Citations are enabled
- [ ] Configuration is saved
- [ ] Test query 1 returns correct red flags with citation
- [ ] Test query 2 recognizes urgent triage with citation
- [ ] Test query 3 provides definition with citation
- [ ] Citations show document ID (e.g., OID-HEADACHE-001)

---

## 🔧 Troubleshooting

### Issue: Datastore Not Listed
**Solution:**
- Go back to Vertex AI Search console
- Verify datastore import status is "Complete"
- Refresh the Dialogflow page
- Try searching for datastore by name

### Issue: No Citations in Response
**Solution:**
- Verify "Citations" checkbox is enabled
- Make sure "Grounding" is also enabled
- Try saving settings again
- Test with a query that explicitly asks for source

### Issue: Agent Not Using Guidelines
**Solution:**
- Check that grounding is enabled
- Verify datastore import completed successfully
- Try query: "According to the guidelines, what are headache red flags?"
- Check datastore has documents in the Data tab

### Issue: Incorrect Information
**Solution:**
- Verify temperature is LOW (0.1-0.3) not high
- Check grounding is enabled (prevents hallucination)
- Test search directly in Vertex AI Search first
- Make sure correct datastore is selected

---

## 📊 Configuration Summary

Once complete, your agent will have:

**Data Source:**
- Datastore: `clinical-guidelines-datastore`
- Documents: 5 clinical guidelines (headache, nausea, dizziness, fatigue, orthostatic hypotension)
- Content: ~45 KB of clinical decision support

**AI Model:**
- Model: Gemini 1.5 Flash
- Temperature: 0.2 (low for consistency)
- Max tokens: 1024

**Features:**
- ✓ Grounding (uses guidelines as source of truth)
- ✓ Citations (shows source documents)
- ✓ Safety filters (blocks harmful content)

**Expected Behavior:**
- Answers based on clinical guidelines
- Cites document ID and source
- Provides appropriate triage recommendations
- Conservative approach (errs on side of caution)

---

## 🎯 Next Steps After Configuration

### Immediate Testing (Today)
1. Test all 15 scenarios from `guidelines/EXAMPLE_SCENARIOS.md`
2. Verify triage accuracy (high/urgent/routine/self-care)
3. Check citation quality (document ID, source, section)
4. Test edge cases (ambiguous symptoms, multiple conditions)

### Refinement (This Week)
1. Adjust prompts if responses need improvement
2. Add more training phrases to intents
3. Fine-tune temperature if responses too rigid or too variable
4. Monitor for any inappropriate or incorrect responses

### Expansion (Next Weeks)
1. Add more clinical guidelines (respiratory, cardiac, etc.)
2. Integrate with appointment scheduling
3. Set up analytics dashboard
4. Conduct user acceptance testing with clinical staff

---

## 📞 Support

**If you get stuck:**
1. Check this guide's troubleshooting section
2. Verify all prerequisites (datastore import complete, etc.)
3. Review `VERTEX_SEARCH_MANUAL_SETUP.md` for search setup
4. Check `guidelines/EXAMPLE_SCENARIOS.md` for test examples

**Console Links:**
- Agent: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039
- Datastore: https://console.cloud.google.com/gen-app-builder/data-stores
- Test Console: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039/test

---

**Time to Complete**: 5-10 minutes  
**Difficulty**: Easy (point and click)  
**Prerequisites**: ✅ Datastore import complete

**Let's finish this! 🚀**

