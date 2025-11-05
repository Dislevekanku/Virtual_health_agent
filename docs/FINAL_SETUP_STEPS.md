# Final Setup Steps - Almost Done!

## ✅ What's Been Created Programmatically

Your agent now has:
- ✅ **6 Intents** with training phrases (symptom_headache, symptom_nausea, etc.)
- ✅ **2 Custom Entity Types** (symptom_type, severity_level)
- ✅ **4 Pages Created**:
  - Symptom Intake (with parameters: symptom_type, duration, severity, additional_symptoms)
  - Clarifying Questions
  - Triage Evaluation (with conditional logic for high/medium/low urgency)
  - Summary
- ✅ **Page Transitions Connected**:
  - Symptom Intake → Clarifying Questions
  - Clarifying Questions → Triage Evaluation
  - Triage Evaluation → Summary

---

## 🔧 One Quick Manual Step Needed (5 minutes)

The script couldn't find the "Start" entry point, so you need to add intent routes manually in the UI. It's super quick!

### Step-by-Step:

1. **Open Your Agent**:
   ```
   https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039
   ```

2. **Go to Build Tab**:
   - Click **Build** in the left sidebar

3. **Click on Default Start Flow**:
   - You'll see the flow canvas
   - Click on the "Default Start Flow" node at the top (not a page, the flow itself)

4. **Edit Entry Fulfillment**:
   - In the right panel, under **Entry fulfillment**
   - Click **+ Add dialogue option** → **Agent says**
   - Enter:
     ```
     Hi — I'm the clinic's virtual assistant. I can help with quick symptom intake so your care team has the right information. What symptoms are you experiencing today?
     ```

5. **Add Intent Routes**:
   - Scroll down in the right panel to **Transition routes**
   - Click **+ Add route** for each intent:

   **Route 1**: symptom_headache
   - Intent: `symptom_headache`
   - Transition to page: `Symptom Intake`
   - Parameter presets: Click **+ Add parameter** → `symptom_type = "headache"`

   **Route 2**: symptom_nausea
   - Intent: `symptom_nausea`
   - Transition to page: `Symptom Intake`
   - Parameter presets: `symptom_type = "nausea"`

   **Route 3**: symptom_dizziness
   - Intent: `symptom_dizziness`
   - Transition to page: `Symptom Intake`
   - Parameter presets: `symptom_type = "dizziness"`

   **Route 4**: symptom_fatigue
   - Intent: `symptom_fatigue`
   - Transition to page: `Symptom Intake`
   - Parameter presets: `symptom_type = "fatigue"`

   **Route 5**: symptom_headache_redflag
   - Intent: `symptom_headache_redflag`
   - Transition to page: `Triage Evaluation`
   - Parameter presets: `urgency = "high"` and `symptom_type = "headache"`

   **Route 6**: symptom_redflag
   - Intent: `symptom_redflag`
   - Transition to page: `Triage Evaluation`
   - Parameter presets: `urgency = "high"`

6. **Click Save**

---

## 🧪 Test Your Agent!

After adding the routes, test immediately!

### Test Console
Click **Test Agent** button (top right of Dialogflow CX console)

### Test Scenarios:

**Test 1: Simple Headache**
```
You: I have a headache
Agent: What is your main symptom?
You: headache
Agent: When did this symptom start?
You: today
Agent: On a scale of 0 to 10, how severe?
You: 3
Agent: Are you experiencing any other symptoms?
You: no
Agent: [Shows low urgency triage and summary]
```

**Test 2: Red Flag (Immediate Escalation)**
```
You: I have a really bad headache and my vision is blurry
Agent: [Should immediately show high urgency message]
```

**Test 3: Nausea**
```
You: I feel nauseous
Agent: [Asks clarifying questions and triages]
```

---

## ✅ Success Checklist

Before marking complete:

- [ ] Agent greets user appropriately
- [ ] Intent `symptom_headache` triggers and routes to Symptom Intake
- [ ] Parameters are collected (symptom, duration, severity)
- [ ] Flow progresses: Symptom Intake → Clarifying → Triage → Summary
- [ ] Triage logic works (high urgency for severity >= 8)
- [ ] Summary displays collected information
- [ ] Red flag intents immediately escalate

---

## 🎯 Alternative: Add Training Phrases to Intents

If intents aren't matching well, you can add more training phrases:

1. Go to **Manage** → **Intents**
2. Click on an intent (e.g., `symptom_headache`)
3. Add more training phrases:
   - "my head hurts"
   - "I have a terrible headache"
   - "headache won't go away"
   etc.
4. Click **Save**

---

## 📊 What's Next

After testing:

1. **Refine**: Add more training phrases based on what doesn't match
2. **Enhance**: Add more symptoms (respiratory, GI, etc.)
3. **Integrate**: Set up webhooks for advanced triage logic
4. **Deploy**: Connect to real systems (appointment scheduling, EHR)
5. **Monitor**: Enable analytics and logging

---

## 🚀 Quick Links

**Your Agent**:
https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

**Test Console**:
https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039/test

---

**Estimated time to complete**: 5-10 minutes  
**Difficulty**: Easy - just adding routes in the UI

You're almost there! 🎉

