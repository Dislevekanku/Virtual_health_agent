# Clinical Guidelines Corpus Setup Guide

## Overview

This guide walks you through setting up a sanitized clinical guideline corpus for your Vertex AI Agent POC. The corpus contains **5 clinical guidelines** covering the symptoms your agent handles: headache, nausea, dizziness, fatigue, and orthostatic hypotension.

**✅ PHI Status**: All content is synthetic with no Protected Health Information (PHI).  
**✅ Ready for POC**: Safe to use for proof-of-concept testing.

---

## 📁 What's Been Created

### Guideline Files (in `/guidelines` folder)

| File | Document ID | Topic | Size |
|------|-------------|-------|------|
| `headache_guideline.txt` | OID-HEADACHE-001 | Headache evaluation & triage | ~8 KB |
| `nausea_vomiting_guideline.txt` | OID-GI-NAUSEA-002 | Nausea/vomiting assessment | ~7 KB |
| `dizziness_vertigo_guideline.txt` | OID-NEURO-DIZZY-003 | Dizziness/vertigo evaluation | ~9 KB |
| `fatigue_guideline.txt` | OID-GEN-FATIGUE-004 | Fatigue workup & management | ~10 KB |
| `orthostatic_hypotension_guideline.txt` | OID-CARDIO-ORTHO-005 | Orthostatic hypotension | ~8 KB |

### Metadata File

- **`guidelines_metadata.json`**: Contains structured metadata for each guideline including:
  - Document ID and title
  - Source and version
  - Keywords for search
  - Citation format
  - GCS path mapping

### Upload Script

- **`upload_to_gcs.py`**: Python script to upload all files to Google Cloud Storage

---

## 🚀 Quick Start: Upload to GCS

### Step 1: Create GCS Bucket

**Option A: Via Console** (recommended for first-time)
1. Go to: https://console.cloud.google.com/storage/create-bucket?project=ai-agent-health-assistant
2. Bucket name: `dfci-guidelines-poc` (or your choice)
3. Location: `us-central1` (same as your agent)
4. Storage class: `Standard`
5. Access control: `Uniform`
6. Click **Create**

**Option B: Via Command Line**
```bash
# Using gcloud
gcloud storage buckets create gs://dfci-guidelines-poc --location=us-central1 --project=ai-agent-health-assistant

# Or using gsutil
gsutil mb -c standard -l us-central1 gs://dfci-guidelines-poc
```

**Option C: Via Python Script**
```bash
python upload_to_gcs.py --bucket dfci-guidelines-poc --create-bucket --project-id ai-agent-health-assistant
```

---

### Step 2: Set Up Credentials

Make sure your service account credentials are configured:

```bash
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS=".\key.json"

# Windows CMD
set GOOGLE_APPLICATION_CREDENTIALS=.\key.json

# macOS/Linux
export GOOGLE_APPLICATION_CREDENTIALS=./key.json
```

---

### Step 3: Upload Guidelines

```bash
python upload_to_gcs.py --bucket dfci-guidelines-poc --verify
```

**Expected Output:**
```
✓ Connected to GCS using credentials from: .\key.json
✓ Found bucket: gs://dfci-guidelines-poc

📁 Found 6 files to upload:
   - headache_guideline.txt
   - nausea_vomiting_guideline.txt
   - dizziness_vertigo_guideline.txt
   - fatigue_guideline.txt
   - orthostatic_hypotension_guideline.txt
   - guidelines_metadata.json

🚀 Uploading to GCS...
   ✓ Uploaded: gs://dfci-guidelines-poc/guidelines/headache_guideline.txt
   ✓ Uploaded: gs://dfci-guidelines-poc/guidelines/nausea_vomiting_guideline.txt
   ...

✅ Successfully uploaded 6 / 6 files
```

---

### Step 4: Verify Upload

```bash
# List bucket contents
python upload_to_gcs.py --bucket dfci-guidelines-poc --list
```

**Or via console:**
https://console.cloud.google.com/storage/browser/dfci-guidelines-poc

---

## 🔍 Setting Up Vertex AI Search

Now integrate your guidelines with Vertex AI Search so your agent can retrieve them.

### Step 1: Create a Datastore

1. **Go to Vertex AI Search & Conversation Console**:
   https://console.cloud.google.com/gen-app-builder/engines?project=ai-agent-health-assistant

2. **Click "Create App"** → **Search**

3. **Configure Search App**:
   - App name: `Clinical Guidelines Search`
   - Company name: `Your Organization` (or leave as default)
   - Location: `Global` or `us-central1`

4. **Create Datastore**:
   - Type: **Unstructured documents**
   - Datastore name: `clinical-guidelines-datastore`

5. **Import Data**:
   - Source: **Cloud Storage**
   - Import format: **Documents**
   - GCS path: `gs://dfci-guidelines-poc/guidelines/*.txt`
     - Include: `headache_guideline.txt`, `nausea_vomiting_guideline.txt`, etc.
     - Exclude: `guidelines_metadata.json` (optional - or include if you want to search metadata)

6. **Import Settings**:
   - Document format: **Plain text**
   - Enable: ✅ **Extract metadata** (if files have structured metadata)
   - Enable: ✅ **Chunk documents** (for better search results)
   - Chunk size: `1000 tokens` (default is fine)

7. **Click Import**

   ⏱️ This takes 5-15 minutes depending on corpus size.

---

### Step 2: Configure Search Settings

Once import completes:

1. **Go to Datastore** → **Search** tab

2. **Enable Features**:
   - ✅ **Snippets**: Show relevant excerpts in results
   - ✅ **Extractive answers**: Extract specific answers from documents
   - ✅ **Citations**: Include source document references

3. **Test Search** (optional but recommended):
   - Query: `What are red flag symptoms for headache?`
   - Expected result: Should return excerpt from `OID-HEADACHE-001` about thunderclap headache, vision changes, etc.

4. **Copy Datastore ID**:
   - You'll need this to connect to your agent
   - Format: `projects/{project}/locations/{location}/collections/default_collection/dataStores/{datastore-id}`

---

### Step 3: Connect to Dialogflow CX Agent

1. **Open Your Agent**:
   https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

2. **Go to "Manage" → "Agent Settings"**

3. **Click "Generative AI" tab**

4. **Enable Data Stores**:
   - Click **+ Add Data Store**
   - Select: `clinical-guidelines-datastore`
   - Enable: ✅ **Citations**

5. **Configure Generation**:
   - Model: `gemini-pro` or `gemini-1.5-flash` (recommended for speed)
   - Temperature: `0.2` (low for clinical accuracy)
   - Enable: ✅ **Grounding** (use datastore as knowledge source)

6. **Save**

---

### Step 4: Update Agent Flows to Use Guidelines

Now configure your agent to query the knowledge base when answering.

#### Option A: Add Generative Fallback

1. **Go to Build → Default Start Flow**

2. **Add Route**:
   - Condition: `true` (fallback)
   - Fulfillment: **Generative AI** → Enable
   - Prompt: 
     ```
     You are a clinical triage assistant. Use the clinical guidelines to answer the patient's question. 
     Always cite the guideline source (document ID and section) when providing information.
     If the question is about symptoms, provide:
     1. Red flag symptoms requiring immediate care
     2. Appropriate triage level
     3. Self-care recommendations if applicable
     
     Format your response clearly and include the citation at the end.
     ```

3. **Save**

#### Option B: Add Knowledge Base Queries to Specific Pages

For each symptom-specific page (e.g., Symptom Intake for Headache):

1. **Edit Page Fulfillment**

2. **Add Parameter Presets** to query guidelines:
   - When `symptom_type = "headache"`, add:
     ```
     Query: "Red flag symptoms for headache requiring emergency evaluation"
     Datastore: clinical-guidelines-datastore
     ```

3. **Use Retrieved Content in Response**:
   ```
   Based on clinical guidelines: $data_store.snippet
   
   Citation: $data_store.title ($data_store.metadata.document_id)
   ```

---

## 📋 Guideline Content Summary

### OID-HEADACHE-001: Headache Evaluation
- **Red Flags**: Thunderclap, vision changes, neurological deficits, post-trauma
- **Triage Levels**: High (ER), Urgent (same-day), Routine, Self-care
- **Key Questions**: Onset, severity (0-10), location, associated symptoms
- **Differential**: Migraine, tension, cluster vs. SAH, meningitis, mass

### OID-GI-NAUSEA-002: Nausea/Vomiting
- **Red Flags**: Hematemesis, severe dehydration, bilious vomiting, acute abdomen
- **Assessment**: Frequency, appearance, hydration status
- **Self-Care**: BRAT diet, clear fluids, ginger
- **Special Populations**: Pregnancy, chemotherapy, pediatric, elderly

### OID-NEURO-DIZZY-003: Dizziness/Vertigo
- **Red Flags**: BEFAST stroke signs, chest pain, focal neuro deficits
- **Types**: Vertigo vs. presyncope vs. disequilibrium
- **Common Causes**: BPPV (most common), orthostatic hypotension, medication
- **Tests**: Dix-Hallpike, orthostatic vitals
- **Safety**: Fall prevention, avoid driving

### OID-GEN-FATIGUE-004: Fatigue
- **Red Flags**: Chest pain, unintentional weight loss, fever >3 days
- **Workup**: CBC, CMP, TSH, B12, vitamin D, HgbA1C
- **Common Causes**: Sleep, depression, anemia, thyroid, diabetes
- **Self-Care**: Sleep hygiene, nutrition, activity, stress management

### OID-CARDIO-ORTHO-005: Orthostatic Hypotension
- **Definition**: BP drop ≥20/10 mmHg within 3 min of standing
- **Red Flags**: Syncope, falls with injury, chest pain
- **Assessment**: Orthostatic vitals (supine → standing at 1 min & 3 min)
- **Management**: Hydration, salt, compression stockings, medications
- **Special Populations**: Elderly, diabetic, Parkinson's

---

## 🎯 Testing Your Setup

### Test 1: Simple Query
**User**: "What are red flag headache symptoms?"

**Expected Agent Response**:
```
According to the Headache Evaluation Guideline (OID-HEADACHE-001), red flag symptoms 
requiring immediate emergency evaluation include:

• Thunderclap headache (worst headache of life)
• Headache with vision changes (double vision, vision loss)
• Headache with neurological deficits (weakness, speech changes)
• Headache after head trauma
• Headache with fever and neck stiffness

If you're experiencing any of these symptoms, please call 911 or go to the 
emergency department immediately.

[Citation: OID-HEADACHE-001, Internal Clinical SOP, Section: Red Flags, Oct 2025]
```

### Test 2: Triage Query
**User**: "I have nausea and vomited twice today"

**Expected Agent Response**:
```
Based on the Nausea and Vomiting Evaluation Guideline (OID-GI-NAUSEA-002), 
vomiting 1-2 episodes per day without signs of dehydration can often be managed 
with self-care initially:

Self-Care Recommendations:
• BRAT diet when able to tolerate (bananas, rice, applesauce, toast)
• Clear fluids: water, electrolyte solution, ginger ale
• Small frequent sips (1-2 oz every 15 minutes)
• Rest and avoid strong odors

When to Seek Care:
• Unable to keep fluids down for 12+ hours
• Persistent vomiting >24 hours
• Signs of dehydration (dark urine, dizziness, confusion)
• Vomiting blood (seek emergency care)

[Citation: OID-GI-NAUSEA-002, Internal Clinical SOP, Section: Self-Care, Oct 2025]
```

### Test 3: Complex Query
**User**: "I feel dizzy when I stand up"

**Expected Agent Response**:
```
Dizziness when standing could be orthostatic hypotension. According to the 
Orthostatic Hypotension Guideline (OID-CARDIO-ORTHO-005):

Definition: Blood pressure drop ≥20/10 mmHg within 3 minutes of standing

This should be evaluated with orthostatic vital signs (blood pressure and heart 
rate while lying down and after standing).

Urgent evaluation is recommended if you have:
• Near-syncope (feeling like you'll faint) or loss of consciousness
• Falls or inability to walk safely
• Symptoms in setting of diabetes or new medications

Safety Measures:
• Sit or lie down immediately if feeling dizzy
• Rise slowly from lying to sitting to standing
• Increase fluid intake (8-10 glasses water/day)
• Avoid sudden position changes

Please schedule an appointment for evaluation within 24-48 hours.

[Citation: OID-CARDIO-ORTHO-005, Internal Clinical SOP, Section: Assessment & Management, Oct 2025]
```

---

## 🔐 Security & Compliance

### PHI Status
- ✅ **All content is synthetic** - No real patient data
- ✅ **No Protected Health Information (PHI)**
- ✅ **Safe for POC testing**

### Before Production Use
- [ ] Clinical validation by medical staff
- [ ] Replace synthetic guidelines with approved internal SOPs
- [ ] HIPAA compliance review
- [ ] Enable audit logging on GCS bucket
- [ ] Set up IAM permissions (least privilege)
- [ ] Encrypt sensitive data (if using real clinical guidelines)

### Access Control

Current setup (POC):
```bash
# Service account has Storage Admin role
# Fine for POC, but restrict for production
```

Production recommendation:
```bash
# Create dedicated service account
gcloud iam service-accounts create vertex-search-sa \
  --project=ai-agent-health-assistant

# Grant read-only access to specific bucket
gsutil iam ch serviceAccount:vertex-search-sa@ai-agent-health-assistant.iam.gserviceaccount.com:objectViewer \
  gs://dfci-guidelines-poc
```

---

## 🔄 Updating Guidelines

### Add New Guideline

1. **Create guideline file**:
   ```bash
   # Example: chest_pain_guideline.txt
   cp guidelines/headache_guideline.txt guidelines/chest_pain_guideline.txt
   # Edit content
   ```

2. **Update metadata**:
   - Add entry to `guidelines/guidelines_metadata.json`

3. **Upload to GCS**:
   ```bash
   python upload_to_gcs.py --bucket dfci-guidelines-poc --verify
   ```

4. **Re-import in Vertex Search**:
   - Go to Datastore → Import
   - Add new file path: `gs://dfci-guidelines-poc/guidelines/chest_pain_guideline.txt`

### Update Existing Guideline

1. **Edit local file**:
   ```bash
   # Update guidelines/headache_guideline.txt
   ```

2. **Update version in metadata**:
   ```json
   {
     "document_id": "OID-HEADACHE-001",
     "version": "1.1",  // increment
     "last_updated": "2025-10"
   }
   ```

3. **Upload (overwrites existing)**:
   ```bash
   python upload_to_gcs.py --bucket dfci-guidelines-poc --verify
   ```

4. **Trigger re-indexing**:
   - Vertex Search auto-detects changes within ~24 hours
   - For immediate: Go to Datastore → Re-import data

---

## 📊 Monitoring & Analytics

### View Search Analytics

1. **Go to Vertex AI Search Console**:
   https://console.cloud.google.com/gen-app-builder/engines?project=ai-agent-health-assistant

2. **Select your Search App**

3. **Click "Analytics" tab**:
   - Query volume
   - Top queries
   - Click-through rate
   - Documents retrieved
   - No-result queries (indicates missing content)

### Key Metrics to Track

- **Search Quality**:
  - Are correct guidelines being retrieved?
  - Are citations accurate?
  - Response time (<2 seconds is good)

- **Coverage**:
  - What queries return no results?
  - Missing guideline topics?

- **Usage**:
  - Which guidelines are queried most?
  - Peak usage times?

---

## 🆘 Troubleshooting

### Upload Issues

**Error**: "Bucket not found"
```bash
# Solution: Create bucket first
python upload_to_gcs.py --bucket dfci-guidelines-poc --create-bucket --project-id ai-agent-health-assistant
```

**Error**: "Permission denied"
```bash
# Solution: Check service account has Storage Admin role
gcloud projects get-iam-policy ai-agent-health-assistant \
  --flatten="bindings[].members" \
  --filter="bindings.members:agent-builder-sa@ai-agent-health-assistant.iam.gserviceaccount.com"
```

### Search Not Returning Results

1. **Check import status**:
   - Console → Datastore → Import tab
   - Status should be "Complete"

2. **Verify files in bucket**:
   ```bash
   gsutil ls -r gs://dfci-guidelines-poc/guidelines/
   ```

3. **Test search directly**:
   - Datastore → Search tab
   - Try simple query: "headache"

4. **Check chunk settings**:
   - If chunks too large, search may not match
   - Re-import with smaller chunk size (500 tokens)

### Agent Not Using Guidelines

1. **Check datastore connected**:
   - Agent Settings → Generative AI → Data stores
   - Should show `clinical-guidelines-datastore`

2. **Enable grounding**:
   - Make sure "Use data store for grounding" is enabled

3. **Test with explicit query**:
   - User input: "Search guidelines for headache red flags"
   - Should trigger datastore query

---

## 📚 Additional Resources

### GCP Documentation
- [Vertex AI Search Overview](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search)
- [Import data from Cloud Storage](https://cloud.google.com/generative-ai-app-builder/docs/create-datastore-ingest)
- [Integrate with Dialogflow CX](https://cloud.google.com/dialogflow/cx/docs/concept/generative)

### Clinical Guideline Sources (for real guidelines)
- UpToDate (subscription required)
- CDC Guidelines: https://www.cdc.gov/
- AHRQ Guidelines: https://www.ahrq.gov/
- Internal SOPs (your organization)

### Vertex AI Agent Builder
- [Agent Builder Console](https://console.cloud.google.com/gen-app-builder)
- [Dialogflow CX Documentation](https://cloud.google.com/dialogflow/cx/docs)

---

## ✅ Success Checklist

Before moving to next phase:

- [ ] GCS bucket created (`dfci-guidelines-poc` or similar)
- [ ] All 5 guideline files uploaded to bucket
- [ ] Metadata file uploaded
- [ ] Vertex AI Search app created
- [ ] Datastore created and data imported (status: Complete)
- [ ] Search tested (returns relevant results)
- [ ] Datastore connected to Dialogflow CX agent
- [ ] Agent tested with guideline queries (returns citations)
- [ ] Security settings reviewed (PHI-free confirmed)

---

## 🎉 You're All Set!

Your clinical guidelines corpus is now ready for your Vertex AI Agent to use!

**What you have**:
- ✅ 5 comprehensive clinical guidelines
- ✅ Structured metadata for citations
- ✅ GCS storage configured
- ✅ Vertex Search integration ready

**Next steps**:
1. Test agent with guideline queries
2. Refine prompts to improve citation formatting
3. Add more guidelines as needed for other symptoms
4. Monitor search analytics to identify gaps

---

**Questions or Issues?**

Refer to:
- `README.md` - Overall project documentation
- `FINAL_SETUP_STEPS.md` - Agent configuration
- GCP Console logs for detailed error messages

**Project**: Virtual Health Assistant POC  
**Created**: October 2025  
**Status**: Ready for POC Testing

