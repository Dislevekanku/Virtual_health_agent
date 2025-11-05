# Step-by-Step UI Guide: Creating the Virtual Health Assistant

This guide walks you through creating the agent using the Google Cloud Console / Agent Builder UI.

---

## Part 1: Initial Setup (5-10 minutes)

### Step 1.1: Navigate to Agent Builder

1. Open browser and go to: https://console.cloud.google.com
2. Select project: **ai-agent-health-assistant**
3. In the search bar, type "Dialogflow CX" or "Agent Builder"
4. Click on **Dialogflow CX** service

### Step 1.2: Create New Agent

1. Click **Create Agent** button
2. Fill in the form:
   ```
   Display name: Virtual-Health-Assistant-POC
   Location: us-central1 (or nearest region)
   Time zone: America/New_York
   Default language: English - en
   ```
3. Under "Description", enter:
   ```
   POC: pre-visit symptom intake & triage (headache, nausea, dizziness, fatigue)
   ```
4. Click **Create**
5. Wait 30-60 seconds for agent provisioning

---

## Part 2: Design Conversation Flow (30-60 minutes)

### Step 2.1: Modify Default Start Flow

1. Click **Build** tab in left sidebar
2. You'll see "Default Start Flow" with "Start" node
3. Click on **Start** node

### Step 2.2: Edit Start Page (Greeting)

1. Click on the **Start** page
2. In the right panel, find "Entry fulfillment"
3. Click **Add dialogue option** → **Agent says**
4. Enter this text:
   ```
   Hi — I'm the clinic's virtual assistant. I can help with quick symptom intake so your care team has the right information. What symptoms are you experiencing today?
   ```
5. Click **Save**

### Step 2.3: Create "Symptom Intake" Page

1. Click **+** button or "Add page"
2. Name it: `Symptom Intake`
3. Click **Create**
4. Select the new "Symptom Intake" page

#### Add Parameters:

1. Scroll to **Form** section
2. Click **Add parameter**

**Parameter 1: symptom_type**
```
Display name: symptom_type
Entity type: @sys.any (for now, we'll create custom later)
Required: ✓ (checked)
Redact in log: ✓ (checked - for HIPAA)
Initial prompt: What is your main symptom?
```

**Parameter 2: duration**
```
Display name: duration
Entity type: @sys.duration
Required: ✓ (checked)
Initial prompt: When did this symptom start? How long have you been experiencing it?
```

**Parameter 3: severity**
```
Display name: severity
Entity type: @sys.number
Required: ✓ (checked)
Initial prompt: On a scale of 0 to 10, how severe is your symptom? (0 = no pain, 10 = worst possible)
```

**Parameter 4: additional_symptoms**
```
Display name: additional_symptoms
Entity type: @sys.any
Is list: ✓ (checked)
Required: ✗ (unchecked)
Initial prompt: Are you experiencing any other symptoms along with this? (You can say "none" if not)
```

5. Click **Save**

### Step 2.4: Create "Clarifying Questions" Page

1. Add another new page: `Clarifying Questions`
2. In **Entry fulfillment**, add text:
   ```
   Thank you for that information. Let me ask a few clarifying questions.
   ```

#### Add Conditional Clarifying Questions:

1. In the "Clarifying Questions" page, scroll to **Routes**
2. Click **Add route**
3. Add condition (for headache red flags):
   ```
   Condition: $session.params.symptom_type = "headache"
   Fulfillment text: Have you noticed any vision changes, confusion, stiff neck, or is this the worst headache you've ever had?
   Parameter to set: red_flag_check = $sys.original-utterance
   ```

4. Add more conditional routes for other symptoms as needed
5. Click **Save**

### Step 2.5: Create "Triage Evaluation" Page

1. Add new page: `Triage Evaluation`
2. This page will use conditional fulfillment

#### Set up Conditional Logic:

1. In **Entry fulfillment**, click **Add dialogue option**
2. Select **Conditional response**
3. Add conditions:

**Condition 1: High Urgency**
```
If: $session.params.severity >= 8
   OR $session.params.red_flag_check CONTAINS "yes"
   OR $session.params.red_flag_check CONTAINS "worst"

Agent says:
"Your symptoms suggest an urgent issue. Please call our nurse line at [INSERT NUMBER] or go to the nearest emergency department. I can connect you to the nurse line now if you'd like."

Set parameters:
- triage = "high"
- recommendation = "Emergency care or nurse line"
```

**Condition 2: Medium Urgency**
```
If: $session.params.severity >= 5 
   OR $session.params.duration >= "3 days"

Agent says:
"I recommend scheduling a same-week visit with your primary care provider or using our telehealth service. Would you like me to help you schedule an appointment?"

Set parameters:
- triage = "medium"
- recommendation = "Same-week appointment or telehealth"
```

**Condition 3: Low Urgency (else)**
```
Else (default):

Agent says:
"This may improve with rest and home care. If symptoms persist beyond 3 days or worsen, please schedule a follow-up with your provider. Monitor your symptoms and reach out if you have concerns."

Set parameters:
- triage = "low"
- recommendation = "Home care and monitoring"
```

4. Click **Save**

### Step 2.6: Create "Summary" Page

1. Add new page: `Summary`
2. In **Entry fulfillment**, add this text:
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
3. Mark as **Final page** (toggle switch)
4. Click **Save**

### Step 2.7: Connect the Pages with Routes

Go back to each page and add transition routes:

**From "Start" page:**
- Condition: `true` (always)
- Transition to: Symptom Intake

**From "Symptom Intake" page:**
- Condition: `$page.params.status = "FINAL"` (all required params collected)
- Transition to: Clarifying Questions

**From "Clarifying Questions" page:**
- Condition: `$page.params.status = "FINAL"`
- Transition to: Triage Evaluation

**From "Triage Evaluation" page:**
- Condition: `true`
- Transition to: Summary

---

## Part 3: Configure Intents (15-30 minutes)

### Step 3.1: Create Custom Intents

1. Click **Manage** tab in left sidebar
2. Click **Intents**
3. Click **Create**

### Create These Intents:

**Intent 1: symptom_headache**
```
Display name: symptom_headache
Training phrases (add these):
- I have a headache
- My head hurts
- I've had a headache for two days
- Headache won't go away
- Head is pounding
- Migraine
```

**Intent 2: symptom_nausea**
```
Display name: symptom_nausea
Training phrases:
- I feel nauseous
- Feeling sick to my stomach
- Can't keep food down
- I'm throwing up
- Nausea since last night
- I feel like vomiting
```

**Intent 3: symptom_dizziness**
```
Display name: symptom_dizziness
Training phrases:
- I feel dizzy
- Lightheaded when I stand
- Room is spinning
- Dizzy when I get up
- Feel unsteady
- Vertigo
```

**Intent 4: symptom_fatigue**
```
Display name: symptom_fatigue
Training phrases:
- I'm exhausted
- So tired all the time
- No energy
- Completely drained
- Can't stay awake
- Fatigued for days
```

**Intent 5: symptom_redflag**
```
Display name: symptom_redflag
Training phrases:
- Chest pain and shortness of breath
- My chest feels tight
- Can't breathe properly
- Severe abdominal pain
- Chest hurts and I'm dizzy
```

### Step 3.2: Add Intent Routes to Start Page

1. Go back to **Build** tab
2. Click on **Start** page
3. Scroll to **Routes** section
4. For each intent created, add a route:

```
Intent: symptom_headache
Transition to: Symptom Intake
Parameter presets: symptom_type = "headache"
```

Repeat for all symptom intents.

---

## Part 4: Configure Fallback Handling (10-20 minutes)

### Step 4.1: Create Fallback Flow

1. In **Build** tab, click **Create flow**
2. Name it: `Fallback Flow`
3. Click **Create**

### Step 4.2: Edit Fallback Page

1. In the Fallback Flow, edit the Start page
2. Add a parameter:
   ```
   Display name: fallback_count
   Entity type: @sys.number
   Default value: 0
   ```

3. Add conditional responses:

**Attempt 1:**
```
If: $session.params.fallback_count = 0

Agent says:
"I'm sorry — I didn't quite catch that. Can you describe your main symptom in one sentence?"

Set parameter: fallback_count = 1
```

**Attempt 2:**
```
If: $session.params.fallback_count = 1

Agent says:
"I'm still having trouble understanding. Would you like to connect to clinic staff directly? I can transfer you to the nurse line."

Set parameter: fallback_count = 2
```

**Attempt 3:**
```
If: $session.params.fallback_count >= 2

Agent says:
"I apologize for the confusion. Let me connect you to our nurse line for personalized assistance."

Transition to: End Flow (or Nurse Line page)
```

### Step 4.3: Configure Default Event Handlers

1. In **Default Start Flow**, scroll to bottom
2. Find **Event handlers** section
3. Add event handler:
   ```
   Event: No-match default
   Transition to flow: Fallback Flow
   ```

---

## Part 5: Test the Agent (10-30 minutes)

### Step 5.1: Open Test Console

1. Click **Test Agent** button (top right)
2. The test panel opens on the right

### Step 5.2: Run Test Scenarios

**Test 1: Simple Headache**
```
You: I have a headache
Agent: [should ask for duration]
You: Started today
Agent: [should ask for severity]
You: About a 3
Agent: [should ask clarifying questions or proceed to triage]
You: No other symptoms
Agent: [should provide low urgency triage and summary]
```

**Test 2: Red Flag**
```
You: I have a really bad headache and my vision is blurry
Agent: [should immediately escalate to high urgency]
```

**Test 3: Fallback**
```
You: zzzzz
Agent: [should ask for clarification]
You: asdf
Agent: [should offer to connect to nurse]
```

### Step 5.3: Review Logs

1. Click on each conversation turn
2. Review:
   - Intent recognition
   - Entity extraction
   - Parameter values
   - Page transitions
3. Make adjustments as needed

---

## Part 6: Adjust & Refine (10-20 minutes)

### Step 6.1: Adjust Tone & Prompts

1. Go to **Manage** → **Agent settings**
2. In "Generative AI" section (if available):
   ```
   System instruction:
   You are a helpful, empathetic virtual health assistant for a clinic. 
   Be calm, professional, and concise. Never provide medical diagnoses 
   or treatment advice. Always escalate urgent symptoms.
   ```

### Step 6.2: Enable Spell Correction

1. In **Agent settings**
2. Toggle **Enable spell correction**: ON

### Step 6.3: Configure Logging

1. In **Agent settings**
2. Toggle **Enable Cloud Logging**: ON
3. Toggle **Enable interaction logging**: ON

---

## QA Checklist

Before marking the agent as "complete", verify:

- [ ] Agent greets user appropriately
- [ ] All 4 main symptom intents are recognized
- [ ] Required parameters are collected (symptom, duration, severity)
- [ ] Clarifying questions are asked when needed
- [ ] Red flag symptoms trigger immediate escalation
- [ ] Triage logic correctly assigns urgency levels
- [ ] Summary includes all collected information
- [ ] Fallback triggers after 1-2 failed attempts
- [ ] Tone is empathetic and professional
- [ ] No medical diagnoses provided
- [ ] Logging is enabled

---

## Next Steps

After completing the UI setup:

1. **Export the agent** (Manage → Export)
2. **Document any customizations** made beyond this guide
3. **Create test report** with results from test scenarios
4. **Share with stakeholders** for feedback
5. **Plan Phase 2** enhancements

---

## Tips for Success

✅ **Save frequently** - changes can be lost if browser crashes
✅ **Test after each page creation** - easier to debug incrementally
✅ **Use descriptive names** - helps with maintenance
✅ **Document custom logic** - add comments in descriptions
✅ **Start simple** - add complexity gradually
✅ **Use version control** - export agent regularly

---

## Troubleshooting

**Issue**: Intent not matching
- **Fix**: Add more diverse training phrases with synonyms

**Issue**: Parameters not filling
- **Fix**: Check entity types and make sure prompts are clear

**Issue**: Page transitions not working
- **Fix**: Verify route conditions and transition targets

**Issue**: Agent repeats questions
- **Fix**: Check parameter names match exactly across pages

---

## Questions or Issues?

Refer to:
- `README.md` for overall project documentation
- `test_scenarios.json` for test cases
- `response_templates.json` for response examples
- [Dialogflow CX Documentation](https://cloud.google.com/dialogflow/cx/docs)

**Created**: October 2025

