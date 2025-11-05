# Next Steps: Complete Your Agent in Dialogflow CX UI

**Status**: ✅ Agent Created Successfully!

**Agent ID**: `72d18125-ac71-4c56-8ea0-44bfc7f9b039`  
**Console Link**: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

---

## What's Already Done ✅

1. **Agent Created**: Virtual-Health-Assistant-POC
2. **Entity Types Created**:
   - `symptom_type` (headache, nausea, dizziness, fatigue, chest_pain)
   - `severity_level` (mild, moderate, severe)
3. **Project APIs Enabled**: All required APIs are active
4. **Service Account Configured**: With all necessary permissions

---

## What You Need to Do Now (30-45 minutes)

### Step 1: Access Your Agent (1 minute)

Click this link or visit manually:
```
https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039
```

You should see your agent dashboard!

---

### Step 2: Create Intents (15-20 minutes)

The script couldn't auto-create intents due to a formatting issue, so we'll add them manually (it's faster anyway).

1. Click **Manage** in left sidebar → **Intents**
2. Click **+ Create** button

**Create these 6 intents with training phrases:**

#### Intent 1: `symptom_headache`
```
Training phrases:
- I have a headache
- My head hurts really bad
- I have a mild headache  
- Headache started this morning
- I've been having headaches for a week
- Head is pounding
- Migraine
- Head pain won't go away
```

#### Intent 2: `symptom_headache_redflag`
```
Training phrases:
- I have a really bad headache and my vision is blurry
- Severe headache with confusion
- Worst headache of my life
- Headache with stiff neck and fever
- Vision changes with my headache
- Sudden severe headache
```

#### Intent 3: `symptom_nausea`
```
Training phrases:
- Feeling nauseous since last night, can't keep food down
- I have mild nausea but no vomiting
- I feel sick to my stomach
- Been throwing up all morning
- Nausea for 3 days
- I feel like vomiting
- Can't eat anything
```

#### Intent 4: `symptom_dizziness`
```
Training phrases:
- I get dizzy when I stand up quickly
- Feeling lightheaded
- The room is spinning
- I feel dizzy and unsteady
- Vertigo symptoms
- Lightheaded all day
```

#### Intent 5: `symptom_fatigue`
```
Training phrases:
- Been exhausted for a week even after sleeping
- I'm so tired all the time
- No energy for days
- Completely drained
- Fatigued and weak
- Can't stay awake
```

#### Intent 6: `symptom_redflag`
```
Training phrases:
- My chest feels tight and I'm lightheaded
- Chest pain and shortness of breath
- I can't breathe properly
- Severe abdominal pain
- Chest hurts and I'm dizzy
```

**Tip**: For each intent, click **Save** before creating the next one.

---

### Step 3: Build Conversation Flow (20-30 minutes)

Now let's create the conversation pages and routes.

1. Click **Build** in left sidebar
2. You'll see "Default Start Flow" with a "Start" page

#### Page 1: Edit "Start" Page (Greeting)

1. Click on the **Start** page
2. In the right panel, find **Entry fulfillment**
3. Click **Add dialogue option** → **Agent says**
4. Enter:
   ```
   Hi — I'm the clinic's virtual assistant. I can help with quick symptom intake so your care team has the right information. What symptoms are you experiencing today?
   ```
5. Scroll down to **Routes** section
6. Click **+ Add route** for each intent:

   **Route 1**:
   - Intent: `symptom_headache`
   - Transition: (we'll create target page next, select "Symptom Intake" when available)
   - Parameter preset: Add `symptom_type = "headache"`

   **Route 2-5**: Repeat for `symptom_nausea`, `symptom_dizziness`, `symptom_fatigue`
   
   **Route 6 (Red flags)**:
   - Intent: `symptom_headache_redflag` OR `symptom_redflag`
   - Transition: "Triage Evaluation" 
   - Parameter preset: Add `urgency = "high"` and `symptom_type = "headache"` or "chest_pain"

7. Click **Save**

#### Page 2: Create "Symptom Intake" Page

1. Click **+** to add new page
2. Name it: `Symptom Intake`
3. In the **Parameters** section, click **+ Add parameter** for each:

   **Parameter 1**:
   ```
   Display name: symptom_type
   Entity type: @symptom_type (custom entity we created)
   Required: ✓
   Redact in log: ✓
   Initial prompt: What is your main symptom?
   ```

   **Parameter 2**:
   ```
   Display name: duration  
   Entity type: @sys.duration
   Required: ✓
   Initial prompt: When did this symptom start? How long have you been experiencing it?
   ```

   **Parameter 3**:
   ```
   Display name: severity
   Entity type: @sys.number
   Required: ✓
   Initial prompt: On a scale of 0 to 10, how severe is your symptom? (0 = no pain, 10 = worst possible)
   ```

   **Parameter 4**:
   ```
   Display name: additional_symptoms
   Entity type: @sys.any
   Is list: ✓
   Required: ✗ (unchecked)
   Initial prompt: Are you experiencing any other symptoms? (Say "none" if not)
   ```

4. Add **Route**:
   - Condition: `$page.params.status = "FINAL"`
   - Transition to: "Clarifying Questions" (create this page next)

5. Click **Save**

#### Page 3: Create "Clarifying Questions" Page

1. Add new page: `Clarifying Questions`
2. **Entry fulfillment**:
   ```
   Thank you. Let me ask a few clarifying questions to better understand your situation.
   ```

3. Add **Parameter**:
   ```
   Display name: red_flag_check
   Entity type: @sys.any
   Required: ✗
   ```

4. Add **Conditional fulfillment**:
   - If: `$session.params.symptom_type = "headache"`
   - Agent says: `Have you noticed any vision changes, confusion, stiff neck, or is this the worst headache you've ever had?`

5. Add **Route**:
   - Condition: `true`
   - Transition to: "Triage Evaluation"

6. Click **Save**

#### Page 4: Create "Triage Evaluation" Page

1. Add new page: `Triage Evaluation`
2. **Entry fulfillment** → **Add conditional response**:

   **Condition 1 (High Urgency)**:
   ```
   If: $session.params.severity >= 8 OR $session.params.urgency = "high" OR $session.params.red_flag_check CONTAINS "yes" OR $session.params.red_flag_check CONTAINS "worst"
   
   Agent says:
   Your symptoms suggest an urgent issue. Please call our nurse line at [INSERT NUMBER] or go to the nearest emergency department. I can connect you to the nurse line now if you'd like.
   
   Set parameters:
   - triage = "high"
   - recommendation = "Emergency care or nurse line"
   ```

   **Condition 2 (Medium Urgency)**:
   ```
   If: $session.params.severity >= 5
   
   Agent says:
   I recommend scheduling a same-week visit with your primary care provider or using our telehealth service. Would you like me to help you schedule an appointment?
   
   Set parameters:
   - triage = "medium"  
   - recommendation = "Same-week appointment or telehealth"
   ```

   **Condition 3 (Low Urgency - else)**:
   ```
   Else:
   
   Agent says:
   This may improve with rest and home care. If symptoms persist beyond 3 days or worsen, please schedule a follow-up with your provider.
   
   Set parameters:
   - triage = "low"
   - recommendation = "Home care and monitoring"
   ```

3. Add **Route**:
   - Condition: `true`
   - Transition to: "Summary"

4. Click **Save**

#### Page 5: Create "Summary" Page

1. Add new page: `Summary`
2. **Entry fulfillment**:
   ```
   Here's a summary of what you've shared:

   Symptom: $session.params.symptom_type
   Duration: $session.params.duration  
   Severity: $session.params.severity out of 10
   Additional Symptoms: $session.params.additional_symptoms
   Triage Level: $session.params.triage
   Recommendation: $session.params.recommendation

   This information will be shared with your care team. Would you like me to check available appointments or connect you to the nurse line?
   ```

3. Toggle **End session** or mark as **End Flow** page

4. Click **Save**

---

### Step 4: Configure Fallback (10 minutes)

1. In "Default Start Flow", scroll to bottom → **Event handlers**
2. Click **+ Add event handler**:
   - Event: `No-match default`
   - Fulfillment: `I'm sorry — I didn't quite catch that. Can you describe your main symptom in one sentence?`

3. Add another event handler:
   - Event: `No-input default`  
   - Fulfillment: `I didn't hear anything. Are you still there?`

4. Click **Save**

---

### Step 5: Configure Agent Settings (5 minutes)

1. Click **Manage** → **Agent Settings**
2. Enable:
   - ✓ **Enable spell correction**
   - ✓ **Enable Cloud Logging**
   - ✓ **Enable interaction logging**

3. In **Generative AI** section (if available), add:
   ```
   You are a helpful, empathetic virtual health assistant. Be calm, professional, and concise. Never provide medical diagnoses or treatment advice. Always escalate urgent symptoms.
   ```

4. Click **Save**

---

## Step 6: Test Your Agent! 🎯

1. Click **Test Agent** button (top right)
2. Try these test conversations:

**Test 1: Simple Headache**
```
You: I have a headache
Agent: [should ask when it started]
You: Started today
Agent: [should ask severity]
You: About a 3
Agent: [should provide low urgency triage]
```

**Test 2: Red Flag**
```
You: I have a really bad headache and my vision is blurry
Agent: [should immediately escalate to high urgency]
```

**Test 3: Nausea**
```
You: Feeling nauseous since last night, can't keep food down
Agent: [should collect info and provide medium urgency]
```

---

## Success Checklist ✅

Before marking complete, verify:

- [ ] Agent greets appropriately
- [ ] All 6 intents are recognized
- [ ] Parameters are collected (symptom, duration, severity)
- [ ] Triage logic works (high/medium/low)
- [ ] Summary displays correctly
- [ ] Fallback responds to unclear inputs
- [ ] Red flags trigger urgent response

---

## Helpful Tips

💡 **Save often** - Changes can be lost if browser crashes  
💡 **Test incrementally** - Test after creating each page  
💡 **Use copy-paste** - For training phrases and responses  
💡 **Check parameter names** - Must match exactly in conditions  

---

## Estimated Time

- Intents: 15-20 min
- Pages & Routes: 20-30 min
- Settings & Testing: 10-15 min
- **Total**: 45-60 minutes

---

## Need Help?

- Full detailed guide: `UI_CREATION_GUIDE.md`
- Test scenarios: `test_scenarios.json`
- Response templates: `response_templates.json`

---

**You're almost there! The agent exists, now just needs the conversation flows.** 🚀

**Agent Console Link**:
https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

