# Connect Clinical Guidelines Datastore - Manual Guide

## Step 1: Create Datastore in Console

1. **Open Vertex AI Search Console:**
   👉 https://console.cloud.google.com/gen-app-builder/data-stores?project=ai-agent-health-assistant

2. **Create New Datastore:**
   - Click **"CREATE DATA STORE"**
   - Select **"Unstructured documents"**
   - Click **"CONTINUE"**

3. **Configure Datastore:**
   - **Data store name**: `clinical-guidelines-datastore`
   - **Region**: `Global` (recommended) or `us-central1`
   - Click **"CREATE"**

4. **Wait for creation** (1-2 minutes)

---

## Step 2: Import Clinical Guidelines

1. **In the datastore page, click "IMPORT DATA"**

2. **Select Data Source:**
   - Choose **"Cloud Storage"**
   - Click **"CONTINUE"**

3. **Select Files:**
   - **Import method**: Select specific files
   - **GCS path**: `gs://dfci-guidelines-poc/guidelines/`
   - Select these files:
     - ✅ `headache_guideline.txt`
     - ✅ `nausea_vomiting_guideline.txt`
     - ✅ `dizziness_vertigo_guideline.txt`
     - ✅ `fatigue_guideline.txt`
     - ✅ `orthostatic_hypotension_guideline.txt`
   - **Exclude**: `guidelines_metadata.json` (optional)

4. **Import Settings:**
   - **Document format**: Plain text
   - ✅ Enable chunking (recommended)
   - ✅ Extract metadata (if available)
   - Click **"IMPORT"**

5. **Wait for import** (5-15 minutes)
   - Monitor progress in the console
   - Status will show "Complete" when done

---

## Step 3: Connect to Dialogflow CX Agent

1. **Open Agent Settings:**
   👉 https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039/settings/generativeAI

2. **Add Data Store:**
   - Scroll to **"Data stores"** section
   - Click **"+ ADD DATA STORE"**
   - Select: `clinical-guidelines-datastore`
   - Click **"SAVE"**

3. **Configure Generative Settings:**
   - **Model**: `gemini-1.5-flash` or `gemini-1.5-pro`
   - **Temperature**: `0.2` (for medical accuracy)
   - ✅ **Enable Grounding**
   - ✅ **Enable Citations**
   - Click **"SAVE"**

---

## Step 4: Update Webhook Code

Once datastore is created, update `rag_simplified.py`:

```python
DATASTORE_ID = "clinical-guidelines-datastore"  # Verify this matches
LOCATION = "global"  # Or "us-central1" if you created it there
```

Then redeploy:
```bash
gcloud functions deploy simplified-rag-webhook --runtime=python311 --region=us-central1 --source=. --entry-point=app --trigger-http --allow-unauthenticated
```

---

## Step 5: Verify Connection

Run this script to verify:
```bash
python connect_datastore_manual_guide.py
```

Or test in Dialogflow Console:
- Go to Test Agent
- Ask: "What are red flag headache symptoms?"
- Should return citations from clinical guidelines

---

## Troubleshooting

### "Datastore not found"
- Check datastore name matches exactly
- Verify location (global vs us-central1)
- Check datastore exists in console

### "Permission denied"
- Service account needs: `Discovery Engine Data Store Viewer` role
- Or: `Discovery Engine Admin` role

### "No results found"
- Wait for import to complete
- Verify files are in GCS bucket
- Check file format is correct

---

**Estimated Time:** 30-45 minutes  
**Status:** Manual process (requires console access)
