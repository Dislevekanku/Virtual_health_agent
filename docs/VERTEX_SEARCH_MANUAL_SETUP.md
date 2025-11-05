# Vertex AI Search Manual Setup Guide

Since the programmatic setup has API complexities, follow these detailed step-by-step instructions to set up Vertex AI Search manually.

---

## ✅ Prerequisites Complete

- ✅ GCS Bucket created: `gs://dfci-guidelines-poc`
- ✅ Guidelines uploaded (5 files + metadata)
- ✅ Service account has Storage Admin role

---

## 📊 Step 1: Create Vertex AI Search App (5 minutes)

### 1.1 Open Vertex AI Search Console
👉 https://console.cloud.google.com/gen-app-builder/engines?project=ai-agent-health-assistant

### 1.2 Create New App
1. Click **"CREATE APP"** button (top right)
2. Select **"Search"** (not Chat)
3. Click **"CONTINUE"**

### 1.3 Configure App
- **App name**: `Clinical Guidelines Search`
- **Company name**: `Your Organization` (or leave as default)
- **Region**: `Global` (recommended) or `us-central1`
- Click **"CONTINUE"**

---

## 📁 Step 2: Create Datastore (3 minutes)

### 2.1 Datastore Configuration
1. On the "Create a data store" page
2. Click **"CREATE NEW DATA STORE"**
3. Select data source: **"Cloud Storage"**
4. Click **"CONTINUE"**

### 2.2 Select Files from Cloud Storage
1. **Import method**: Select specific files
2. Click **"BROWSE"** 
3. Navigate to: `dfci-guidelines-poc` → `guidelines/`
4. Select all `.txt` files (do NOT select the .json file):
   - ✅ `headache_guideline.txt`
   - ✅ `nausea_vomiting_guideline.txt`
   - ✅ `dizziness_vertigo_guideline.txt`
   - ✅ `fatigue_guideline.txt`
   - ✅ `orthostatic_hypotension_guideline.txt`
   - ❌ `guidelines_metadata.json` (skip this)
5. Click **"SELECT"**

### 2.3 Configure Datastore Settings
- **Data store name**: `clinical-guidelines-datastore`
- **Data type**: **Unstructured documents**
- **Region**: Same as app (Global or us-central1)
- Advanced options:
  - ✅ **Enable chunking** (recommended)
  - Chunk size: `1000` tokens (default is fine)
  - ✅ **Enable metadata extraction**
- Click **"CREATE"**

---

## ⏳ Step 3: Wait for Import (10-15 minutes)

### 3.1 Monitor Import Status
1. You'll see "Importing data..." screen
2. Status will show:
   - "Importing" → "Processing" → "Complete"
3. This typically takes **10-15 minutes** for 5 documents

### 3.2 While Waiting
You can:
- Continue reading this guide
- Prepare your Dialogflow agent
- Get coffee ☕

### 3.3 Verify Import Completion
1. Once status shows **"Complete"**
2. Click on the datastore name
3. Go to **"Data"** tab
4. You should see **5 documents** listed

---

## 🔍 Step 4: Configure Search Settings (2 minutes)

### 4.1 Enable Search Features
1. Go to your datastore
2. Click **"Configurations"** tab
3. Enable the following:
   - ✅ **Snippets**: Show relevant excerpts
   - ✅ **Extractive answers**: Extract specific answers
   - ✅ **Extractive segments**: Longer text segments
   - ✅ **Answer generation** (if available - uses LLM)

### 4.2 Configure Boost/Bury (Optional)
- Can skip this for POC
- Used to prioritize certain documents or keywords

### 4.3 Save Settings
- Click **"SAVE"**

---

## 🧪 Step 5: Test Search (3 minutes)

### 5.1 Go to Search Tab
1. In your datastore, click **"Search"** tab
2. You'll see a search box

### 5.2 Test Queries
Try these test queries:

**Test 1: Red Flags**
```
What are red flag symptoms for headache?
```
**Expected**: Should return excerpts about thunderclap headache, vision changes, neurological deficits

**Test 2: Triage**
```
When should someone with nausea see a doctor urgently?
```
**Expected**: Should return info about persistent vomiting >24 hours, dehydration

**Test 3: Specific Condition**
```
What is orthostatic hypotension?
```
**Expected**: Should return definition and blood pressure drop criteria

### 5.3 Review Results
- Check that results are relevant
- Verify citations show document names
- Look at quality scores (should be > 0.5 for good matches)

---

## 🤖 Step 6: Connect to Dialogflow CX Agent (5 minutes)

### 6.1 Open Your Agent
👉 https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

### 6.2 Go to Agent Settings
1. Click **"Manage"** in left sidebar
2. Click **"Agent Settings"**
3. Click **"Generative AI"** tab

### 6.3 Add Data Store
1. Scroll to **"Data stores"** section
2. Click **"+ ADD DATA STORE"**
3. Select `clinical-guidelines-datastore`
4. Click **"SAVE"**

### 6.4 Configure Generative Settings
1. **Model**: Select `gemini-1.5-flash` (recommended for speed and cost)
   - Alternative: `gemini-1.5-pro` (more accurate but slower/costlier)
2. **Temperature**: `0.2` (low for clinical accuracy and consistency)
3. **Max output tokens**: `1024` (default is fine)
4. **Top K**: `40` (default is fine)
5. **Top P**: `0.95` (default is fine)

### 6.5 Enable Features
✅ **Grounding**: Use data store for factual responses
✅ **Citations**: Include source references in responses
✅ **Safety settings**: Keep at default (block harmful content)

### 6.6 Save Configuration
- Click **"SAVE"** at bottom

---

## 🎯 Step 7: Test Agent with Knowledge Base (5 minutes)

### 7.1 Open Test Agent
1. Click **"Test Agent"** button (top right of Dialogflow console)
2. Or go to: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039/test

### 7.2 Test Guideline Queries

**Test 1: Direct Guideline Query**
```
User: What are red flag headache symptoms?
```
**Expected Response**: Should cite OID-HEADACHE-001 and list:
- Thunderclap headache
- Vision changes
- Neurological deficits
- Fever + neck stiffness
- Post head trauma

**Test 2: Triage Query**
```
User: I've been vomiting for 2 days and can't keep water down
```
**Expected Response**: Should recognize urgent evaluation needed, cite OID-GI-NAUSEA-002

**Test 3: Complex Query**
```
User: I get dizzy when I stand up quickly
```
**Expected Response**: Should mention orthostatic hypotension, cite OID-CARDIO-ORTHO-005

### 7.3 Verify Citations
- Look for citations in agent responses
- Should show document ID (e.g., OID-HEADACHE-001)
- Should show source (Internal Clinical SOP)
- May show specific page or section

---

## ✅ Success Checklist

Before marking setup complete:

- [ ] Vertex AI Search app created
- [ ] Datastore created (`clinical-guidelines-datastore`)
- [ ] All 5 guideline files imported successfully
- [ ] Import status shows "Complete"
- [ ] Search test returns relevant results
- [ ] Datastore connected to Dialogflow agent
- [ ] Generative AI configured (model, temperature, etc.)
- [ ] Citations enabled
- [ ] Grounding enabled
- [ ] Agent test shows guideline content in responses
- [ ] Citations appear in agent responses

---

## 🔧 Troubleshooting

### Issue: Import Stuck or Failed
**Solution**:
1. Check file format (must be .txt)
2. Verify files are in GCS bucket
3. Try importing files one at a time
4. Check service account has Storage Object Viewer role

### Issue: Search Returns No Results
**Solution**:
1. Wait for import to fully complete (status = "Complete")
2. Check documents are visible in Data tab
3. Try simpler query (e.g., just "headache")
4. Verify chunk settings enabled

### Issue: Agent Not Using Guidelines
**Solution**:
1. Verify datastore is connected (Agent Settings → Generative AI → Data stores)
2. Make sure "Grounding" is enabled
3. Check that import completed successfully
4. Try more specific query that should match guideline content

### Issue: No Citations in Responses
**Solution**:
1. Enable "Citations" in Agent Settings → Generative AI
2. Make sure "Grounding" is also enabled
3. Try query that directly asks for source
4. Check that documents have metadata

---

## 📊 Monitoring & Analytics

### View Search Analytics
1. Go to datastore
2. Click **"Analytics"** tab
3. Review:
   - **Query volume**: How many searches
   - **Top queries**: What users are searching for
   - **No-result queries**: Gaps in coverage
   - **Click-through rate**: Are results relevant?

### Dialogflow Analytics
1. In Dialogflow agent, go to **"Manage" → "Analytics"**
2. Review:
   - **Session flows**: User conversation paths
   - **Intents triggered**: What intents are matching
   - **Parameters collected**: Data quality
   - **Containment rate**: How many queries agent handled

---

## 🎓 Best Practices

### For Better Search Results
1. **Use descriptive document names** (already done)
2. **Enable chunking** for large documents
3. **Add metadata** for better filtering
4. **Test regularly** with real user queries
5. **Monitor no-result queries** to identify gaps

### For Better Agent Responses
1. **Keep temperature low** (0.1-0.3) for clinical accuracy
2. **Always enable grounding** to reduce hallucinations
3. **Enable citations** for transparency
4. **Test edge cases** (ambiguous symptoms, multiple conditions)
5. **Monitor for inappropriate responses**

---

## 📈 Next Steps After Setup

### Immediate (This Week)
1. Test with all 15 scenarios from `EXAMPLE_SCENARIOS.md`
2. Validate accuracy of triage recommendations
3. Check citation quality and formatting
4. Identify any missing guideline content

### Short-Term (This Month)
1. Add more guidelines (respiratory, cardiac, etc.)
2. Refine agent prompts for better citation formatting
3. Set up regular monitoring/analytics review
4. Conduct user acceptance testing with clinical staff

### Long-Term (Production)
1. Replace synthetic guidelines with validated clinical protocols
2. Clinical validation of all agent responses
3. HIPAA compliance review
4. Enable audit logging
5. Production deployment planning

---

## 📞 Support Resources

### Documentation
- [Vertex AI Search Docs](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search)
- [Dialogflow CX Docs](https://cloud.google.com/dialogflow/cx/docs)
- [Grounding with Search](https://cloud.google.com/dialogflow/cx/docs/concept/generative)

### Console Links
- **Vertex Search**: https://console.cloud.google.com/gen-app-builder/engines
- **Dialogflow CX**: https://dialogflow.cloud.google.com/cx
- **GCS Bucket**: https://console.cloud.google.com/storage/browser/dfci-guidelines-poc

---

## ⏱️ Time Estimate

| Step | Task | Time |
|------|------|------|
| 1 | Create Vertex AI Search app | 5 min |
| 2 | Create datastore & import | 3 min |
| 3 | Wait for import completion | 10-15 min |
| 4 | Configure search settings | 2 min |
| 5 | Test search | 3 min |
| 6 | Connect to Dialogflow agent | 5 min |
| 7 | Test agent | 5 min |
| **Total** | **Active time** | **~25 min** |
| **Total** | **Including wait time** | **~35-40 min** |

---

**Status**: Ready to begin  
**Prerequisites**: ✅ All complete  
**Difficulty**: Medium (mostly pointing and clicking)

**Good luck! 🚀**

