# Example Patient Scenarios (Synthetic - No PHI)

These are **synthetic patient scenarios** for POC testing. Use these to test your agent's ability to triage symptoms and cite clinical guidelines appropriately.

---

## Scenario 1: High Urgency - Thunderclap Headache

**Patient Input**: "I suddenly have the worst headache of my life. It came on really fast about 10 minutes ago."

**Expected Agent Behavior**:
- ✅ Immediately recognize red flag (thunderclap headache)
- ✅ Escalate to emergency (911/ED)
- ✅ Cite OID-HEADACHE-001, Section: Red Flags
- ❌ Do NOT suggest scheduling appointment
- ❌ Do NOT recommend self-care

**Expected Response**:
```
🚨 EMERGENCY - IMMEDIATE ACTION REQUIRED

Based on your symptoms, you need immediate emergency care. A sudden, severe 
"worst headache of life" is a red flag that requires urgent evaluation.

According to the Headache Evaluation Guideline (OID-HEADACHE-001):
"Sudden onset thunderclap headache (worst headache of life) requires 
IMMEDIATE evaluation. Call 911 or go to the emergency department immediately."

ACTION: Please call 911 or have someone drive you to the nearest emergency 
department right away. Do not delay.

[Citation: OID-HEADACHE-001, Internal Clinical SOP, Section: Red Flags, Oct 2025]
```

---

## Scenario 2: Routine - Mild Headache

**Patient Input**: "I have a mild headache, maybe 3 out of 10. Started this morning. No other symptoms."

**Expected Agent Behavior**:
- ✅ Assess severity (3/10 = mild)
- ✅ Check duration (<24 hours)
- ✅ Recommend self-care initially
- ✅ Provide safety net advice
- ✅ Cite guideline self-care section

**Expected Response**:
```
Based on your symptoms, this sounds like a mild headache that may respond to 
self-care measures.

According to the Headache Evaluation Guideline (OID-HEADACHE-001), 
for mild headaches (severity 1-3/10) present less than 72 hours:

Self-Care Recommendations:
• Rest in a quiet, dark environment
• Stay well hydrated (8-10 glasses of water today)
• Over-the-counter pain relief: Acetaminophen 500-1000mg or Ibuprofen 400-600mg
• Apply a cold compress to your forehead
• Avoid bright lights, loud noises, and screens

When to Seek Care:
• Headache persists beyond 3 days
• Severity increases (becomes >6/10)
• New symptoms develop (vision changes, nausea, fever)
• You develop any warning signs like sudden worsening or neurological symptoms

Would you like me to schedule a follow-up appointment, or do you have any questions 
about these recommendations?

[Citation: OID-HEADACHE-001, Internal Clinical SOP, Section: Self-Care, Oct 2025]
```

---

## Scenario 3: Urgent - Persistent Vomiting

**Patient Input**: "I've been throwing up all day yesterday and today. Can't keep anything down. Feeling really weak."

**Expected Agent Behavior**:
- ✅ Recognize persistent vomiting >24 hours
- ✅ Assess hydration status (unable to keep fluids down)
- ✅ Urgent same-day evaluation needed
- ✅ Cite OID-GI-NAUSEA-002, Urgent Evaluation section

**Expected Response**:
```
⚡ URGENT EVALUATION NEEDED

Persistent vomiting for over 24 hours with inability to keep fluids down requires 
same-day medical evaluation.

According to the Nausea and Vomiting Evaluation Guideline (OID-GI-NAUSEA-002):
"Persistent vomiting >24 hours or unable to tolerate oral fluids for 12+ hours 
requires urgent same-day appointment. Risk of dehydration increases significantly."

You need to be seen today for:
• Hydration status assessment
• Possible IV fluids
• Anti-nausea medication
• Evaluation for underlying cause

ACTION: I'm going to connect you with our nurse line for immediate assessment and 
scheduling of a same-day appointment or urgent care visit.

Until you're seen:
• Continue trying small sips of water or electrolyte solution (1-2 oz every 15 min)
• Avoid solid foods
• Rest

Seek Emergency Care If:
• You vomit blood
• You become confused or extremely dizzy
• You have severe abdominal pain
• You have no urine output for 12+ hours

[Citation: OID-GI-NAUSEA-002, Internal Clinical SOP, Section: Urgent Evaluation, Oct 2025]
```

---

## Scenario 4: Assessment - Orthostatic Symptoms

**Patient Input**: "I get dizzy when I stand up. Happens most mornings. I'm diabetic and take blood pressure meds."

**Expected Agent Behavior**:
- ✅ Recognize orthostatic symptoms
- ✅ Note risk factors (diabetes, BP meds)
- ✅ Recommend orthostatic vital signs check
- ✅ Same-day evaluation
- ✅ Cite OID-CARDIO-ORTHO-005

**Expected Response**:
```
⚡ SAME-DAY EVALUATION RECOMMENDED

Dizziness when standing (especially in someone with diabetes and on blood pressure 
medications) could be orthostatic hypotension and should be evaluated.

According to the Orthostatic Hypotension Guideline (OID-CARDIO-ORTHO-005):

Definition: Orthostatic hypotension is a blood pressure drop of ≥20/10 mmHg 
within 3 minutes of standing, which can cause dizziness, lightheadedness, 
or fainting.

Risk Factors You Have:
• Diabetes (autonomic neuropathy risk)
• Blood pressure medications (can contribute to orthostatic hypotension)

Recommended Evaluation:
You should have orthostatic vital signs checked (blood pressure and heart rate 
measured while lying down and after standing). This requires an in-person visit.

Safety Measures (Until Evaluated):
• Rise slowly: Sit on edge of bed for 1 minute before standing
• Sit or lie down immediately if you feel dizzy
• Increase fluid intake (8-10 glasses water/day)
• Don't drive or operate machinery while experiencing symptoms
• Remove fall hazards at home

When to Seek Emergency Care:
• If you lose consciousness
• If you fall and injure yourself
• If you have chest pain with the dizziness

ACTION: Let's schedule a same-day or next-available appointment for orthostatic 
vital sign measurement and medication review.

[Citation: OID-CARDIO-ORTHO-005, Internal Clinical SOP, Section: Assessment & Management, Oct 2025]
```

---

## Scenario 5: Complex - Fatigue Workup

**Patient Input**: "I've been exhausted for about 6 weeks now. Getting 8 hours of sleep but still tired all day. It's affecting my work."

**Expected Agent Behavior**:
- ✅ Recognize chronic fatigue (>4 weeks)
- ✅ Note functional impact (affecting work)
- ✅ Recommend lab workup
- ✅ Schedule within 1 week
- ✅ Cite OID-GEN-FATIGUE-004

**Expected Response**:
```
📅 EVALUATION RECOMMENDED WITHIN 1 WEEK

Persistent fatigue lasting 6 weeks that is interfering with your work should be 
evaluated to identify any underlying medical causes.

According to the Fatigue Evaluation Guideline (OID-GEN-FATIGUE-004):

Fatigue >4 weeks without a clear cause warrants:
• Comprehensive history and physical exam
• Laboratory workup to rule out common causes

Recommended Laboratory Tests:
• Complete Blood Count (CBC) - check for anemia
• Comprehensive Metabolic Panel (CMP) - kidney, liver, glucose
• Thyroid function (TSH) - hypothyroidism is a common cause
• Vitamin B12 and Vitamin D levels
• Hemoglobin A1C (diabetes screening)

Common Causes of Chronic Fatigue:
• Anemia (iron, B12, or folate deficiency)
• Hypothyroidism
• Diabetes
• Depression or anxiety
• Sleep disorders (sleep apnea)
• Chronic stress or burnout

Assessment Questions:
Before your appointment, it may be helpful to note:
• Sleep quality (do you wake feeling rested?)
• Mood changes (feeling down, anxious, or unmotivated?)
• Other symptoms (weight change, cold intolerance, pain, cognitive issues)
• Medications and supplements you're taking
• Recent major life stressors

In the Meantime - Self-Care:
• Maintain consistent sleep schedule (same bedtime/wake time)
• Eat balanced meals with adequate protein
• Light exercise if energy permits (even 10-minute walks can help)
• Manage stress (meditation, breaks during work)
• Stay hydrated

When to Seek Urgent Care:
• If you develop chest pain or shortness of breath
• If you have severe weakness (unable to perform daily tasks)
• If you experience confusion or altered mental status

ACTION: Let's schedule an appointment within the next week for evaluation and 
lab work. Would you prefer in-person or telehealth initial visit?

[Citation: OID-GEN-FATIGUE-004, Internal Clinical SOP, Section: Evaluation & Workup, Oct 2025]
```

---

## Scenario 6: Red Flag - BEFAST Stroke Signs

**Patient Input**: "I feel really dizzy and my left arm feels weak. My speech sounds funny."

**Expected Agent Behavior**:
- ✅ IMMEDIATE recognition of stroke warning signs (BEFAST)
- ✅ Urgent 911 escalation
- ✅ Cite OID-NEURO-DIZZY-003, Stroke Assessment
- ❌ Do NOT delay for any reason

**Expected Response**:
```
🚨🚨 EMERGENCY - CALL 911 IMMEDIATELY 🚨🚨

Your symptoms suggest a possible STROKE. This is a medical emergency.

According to the Dizziness and Vertigo Evaluation Guideline (OID-NEURO-DIZZY-003):

BEFAST Stroke Warning Signs:
✓ Balance loss (dizziness) - YOU HAVE THIS
✓ Eyesight changes
✓ Face drooping
✓ Arm weakness - YOU HAVE THIS
✓ Speech difficulty - YOU HAVE THIS
✓ Time to call 911

IMMEDIATE ACTION REQUIRED:
1. Call 911 right now
2. Tell them you have stroke symptoms
3. Do not drive yourself
4. Note the time symptoms started (this is important for treatment)

If you're not alone, have someone help you while calling 911.

TIME IS CRITICAL: Stroke treatment is most effective within the first few hours.

[Citation: OID-NEURO-DIZZY-003, Internal Clinical SOP, Section: Red Flags & Stroke Assessment, Oct 2025]
```

---

## Scenario 7: Self-Care - Positional Vertigo (BPPV)

**Patient Input**: "When I roll over in bed, I get a spinning sensation for about 30 seconds. This has happened a few times before."

**Expected Agent Behavior**:
- ✅ Recognize classic BPPV presentation
- ✅ Assess severity and duration
- ✅ Can consider self-care if mild and recurrent known diagnosis
- ✅ Recommend evaluation if first episode or severe
- ✅ Cite OID-NEURO-DIZZY-003, BPPV section

**Expected Response**:
```
This sounds like it could be Benign Paroxysmal Positional Vertigo (BPPV), 
a common and treatable cause of dizziness.

According to the Dizziness and Vertigo Evaluation Guideline (OID-NEURO-DIZZY-003):

BPPV Characteristics:
• Brief episodes of vertigo (spinning sensation)
• Triggered by specific head positions (rolling over, looking up)
• Lasts seconds to minutes
• Most common cause of vertigo

Since you mentioned this has happened before, it may be a recurrence. However, 
I'd like to ask a few more questions to make sure:

Assessment Questions:
1. Have you been formally diagnosed with BPPV before?
2. Is this the same pattern as previous episodes?
3. Do you have any other symptoms (hearing loss, ringing in ears, headache, weakness)?
4. Are you able to walk safely?
5. Have you had any recent head injury?

If this is a known BPPV recurrence:
• Epley maneuver (canalith repositioning) can be helpful
• Your provider may have taught you this previously
• Avoid sudden head movements
• Symptoms often resolve in days to weeks

Recommendation:
Even though this may be BPPV, I recommend scheduling an appointment within the 
next few days for confirmation and treatment. The Epley maneuver performed in 
the office is 80% effective for BPPV.

Safety Measures:
• Avoid driving if you're having active symptoms
• Use handrails on stairs
• Sit or lie down if vertigo occurs
• Remove fall hazards at home

Seek Urgent Care If:
• Symptoms worsen or become constant
• You develop hearing loss (new or sudden)
• You have difficulty walking
• You develop neurological symptoms (weakness, numbness, speech changes)

Would you like me to schedule an appointment for BPPV evaluation?

[Citation: OID-NEURO-DIZZY-003, Internal Clinical SOP, Section: BPPV & Differential Diagnosis, Oct 2025]
```

---

## Scenario 8: Medication Review - Nausea on New Medication

**Patient Input**: "I started a new antibiotic 3 days ago and I've been nauseous ever since. Haven't thrown up but feel queasy."

**Expected Agent Behavior**:
- ✅ Recognize medication-induced nausea
- ✅ Assess severity (nausea without vomiting = less urgent)
- ✅ Recommend routine evaluation / medication review
- ✅ Provide interim self-care
- ✅ Cite OID-GI-NAUSEA-002, Medication considerations

**Expected Response**:
```
It sounds like your nausea may be related to your new antibiotic. This is a 
common side effect of many antibiotics.

According to the Nausea and Vomiting Evaluation Guideline (OID-GI-NAUSEA-002):

Medication-Related Nausea:
Nausea associated with new medication changes should be evaluated, especially 
if it interferes with medication compliance or quality of life.

Questions:
1. What antibiotic were you prescribed? (e.g., amoxicillin, azithromycin, ciprofloxacin)
2. Are you taking it with food? (many antibiotics are better tolerated with food)
3. What is the antibiotic treating? (important to know if it's essential to complete)
4. How severe is the nausea (0-10 scale)?

Recommendations:
• Contact your prescribing provider or pharmacist within 24-48 hours
• They can advise whether to:
  - Continue with strategies to reduce nausea (take with food, smaller meals)
  - Switch to a different antibiotic
  - Add an anti-nausea medication
  - Adjust the dose or timing

Self-Care (In the Meantime):
• Take medication with food (unless label says otherwise)
• Eat small, frequent meals rather than large meals
• Avoid fatty or spicy foods
• Ginger tea or ginger candies may help
• Stay hydrated with clear fluids

Important:
• Do not stop the antibiotic without talking to your provider
  (incomplete antibiotic courses can lead to resistant infections)
• If you start vomiting and can't keep the antibiotic down, contact provider same-day

Seek Urgent Care If:
• You develop vomiting (can't keep medication down)
• You have severe abdominal pain
• You develop rash or difficulty breathing (allergic reaction - go to ED)
• You become dehydrated

ACTION: I recommend scheduling a phone call or telehealth visit with your provider 
within 24-48 hours for medication review.

[Citation: OID-GI-NAUSEA-002, Internal Clinical SOP, Section: Medication Considerations, Oct 2025]
```

---

## Testing Tips

### Use These Scenarios To Test:

1. **Red Flag Recognition**: Scenarios 1, 6 (should escalate to 911 immediately)
2. **Triage Accuracy**: Scenarios 2, 3, 4, 5 (appropriate urgency level)
3. **Guideline Citation**: All scenarios (should include proper citations)
4. **Clinical Reasoning**: Scenario 7, 8 (asks clarifying questions)
5. **Safety Netting**: All scenarios (provides warning signs to watch for)

### Expected Agent Behaviors:

✅ **DO**:
- Cite specific guideline (document ID, section)
- Provide clear action (emergency, urgent, routine, self-care)
- Include safety net advice ("seek care if...")
- Ask clarifying questions when appropriate
- Recognize red flags immediately
- Provide evidence-based recommendations

❌ **DON'T**:
- Give definitive diagnosis
- Prescribe medications
- Delay emergency care for red flags
- Ignore important symptoms
- Provide vague advice
- Fail to cite sources

---

## Additional Test Scenarios (Quick)

| # | Input | Expected Triage | Key Citation |
|---|-------|-----------------|--------------|
| 9 | "Headache + fever + stiff neck" | 🚨 Emergency (meningitis) | OID-HEADACHE-001, Red Flags |
| 10 | "Vomiting blood" | 🚨 Emergency | OID-GI-NAUSEA-002, Red Flags |
| 11 | "Tired for 2 days after working late" | 🏠 Self-care | OID-GEN-FATIGUE-004, Self-Care |
| 12 | "Dizzy in patient age 70 after falling yesterday" | ⚡ Urgent same-day | OID-NEURO-DIZZY-003, Elderly |
| 13 | "Headache 5/10 for 5 days, not getting better with Tylenol" | ⚡ Urgent | OID-HEADACHE-001, Urgent Evaluation |
| 14 | "Nausea in pregnancy, vomiting 3x today" | ⚡ Urgent (hyperemesis risk) | OID-GI-NAUSEA-002, Special Populations |
| 15 | "Fatigue + yellow skin" | 🚨 Emergency (jaundice) | OID-GEN-FATIGUE-004, Red Flags |

---

**Document**: Example Patient Scenarios  
**Purpose**: POC Testing - Agent Validation  
**Created**: October 2025  
**Status**: All scenarios are SYNTHETIC (no real PHI)

