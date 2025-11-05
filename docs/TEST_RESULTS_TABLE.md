## Test Results Table

| Scenario ID | Input | Intent Recognized | Triage Level | Recommendation | Status |
|-------------|-------|-------------------|--------------|----------------|--------|
| test_001 | I have a headache | symptom_headache | Not set (expected: low) | Not provided | ❌ FAIL |
| test_002 | I have a really bad headache and my vision is blur | symptom_headache_redflag | Not set (expected: high) | Not provided | ❌ FAIL |
| test_003 | Feeling nauseous since last night, can't keep food | symptom_nausea | Not set (expected: medium) | Not provided | ❌ FAIL |
| test_004 | I get dizzy when I stand up quickly | symptom_dizziness | Not set (expected: medium) | Not provided | ❌ FAIL |
| test_005 | Been exhausted for a week even after sleeping | symptom_fatigue | Not set (expected: medium) | Not provided | ❌ FAIL |
| test_006 | My chest feels tight and I'm lightheaded | symptom_redflag | Not set (expected: high) | Not provided | ❌ FAIL |
| test_007 | I don't feel good | None | Not set (expected: n/a) | Not provided | ✅ PASS |
| test_008 | zzzzz | None | Not set (expected: n/a) | Not provided | ✅ PASS |

## Detailed Results

### Simple Headache - Low Urgency (test_001)

**Description:** Patient with mild headache, short duration

**Expected Triage:** low

**Conversation Flow:**

**Turn 1:**
- User: I have a headache
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_headache (confidence: 1.00)
- Page: Symptom Intake

**Turn 2:**
- User: It started this morning
- Agent: On a scale of 0 to 10, where 0 means no pain or discomfort and 10 means the worst possible pain, how would you rate your symptoms? You can say the number, like '3' or 'about 7'....
- Intent: None (confidence: 0.20)
- Page: Symptom Intake

**Turn 3:**
- User: About a 3 out of 10
- Agent: Thank you for providing those details. Let me ask a few clarifying questions to better understand your situation and determine the appropriate level of care....
- Intent: None (confidence: 0.20)
- Page: Summary

**Turn 4:**
- User: No other symptoms
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_dizziness (confidence: 0.74)
- Page: Summary

**Final Triage:** None

**Final Recommendation:** None

**Status:** ❌ FAILED

**Errors:**
- Triage mismatch: expected 'low', got 'None'

---

### Red Flag Headache - High Urgency (test_002)

**Description:** Patient with severe headache and vision changes

**Expected Triage:** high

**Conversation Flow:**

**Turn 1:**
- User: I have a really bad headache and my vision is blurry
- Agent: Based on your symptoms, I'm evaluating the appropriate level of care you need....
- Intent: symptom_headache_redflag (confidence: 1.00)
- Page: Summary

**Final Triage:** None

**Final Recommendation:** None

**Status:** ❌ FAILED

**Errors:**
- Turn 1: Missing parameter 'symptom'
- Turn 1: Missing parameter 'vision_change'
- Triage mismatch: expected 'high', got 'None'

---

### Nausea with Vomiting - Medium Urgency (test_003)

**Description:** Patient unable to keep food down

**Expected Triage:** medium

**Conversation Flow:**

**Turn 1:**
- User: Feeling nauseous since last night, can't keep food down
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_nausea (confidence: 1.00)
- Page: Symptom Intake

**Turn 2:**
- User: The nausea is about a 6
- Agent: When did your symptoms begin? For example, 'this morning', '2 days ago', 'last week', or 'about 3 days'....
- Intent: None (confidence: 0.20)
- Page: Symptom Intake

**Turn 3:**
- User: I can drink water but nothing stays down
- Agent: When did your symptoms begin? For example, 'this morning', '2 days ago', 'last week', or 'about 3 days'....
- Intent: None (confidence: 0.20)
- Page: Symptom Intake

**Final Triage:** None

**Final Recommendation:** None

**Status:** ❌ FAILED

**Errors:**
- Turn 1: Missing parameter 'symptom'
- Turn 1: Missing parameter 'duration'
- Turn 1: Missing parameter 'vomiting'
- Triage mismatch: expected 'medium', got 'None'

---

### Positional Dizziness - Medium Urgency (test_004)

**Description:** Patient with dizziness when standing

**Expected Triage:** medium

**Conversation Flow:**

**Turn 1:**
- User: I get dizzy when I stand up quickly
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_dizziness (confidence: 1.00)
- Page: Symptom Intake

**Turn 2:**
- User: It's been happening for about 3 days
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_nausea (confidence: 0.40)
- Page: Symptom Intake

**Turn 3:**
- User: Maybe a 5 out of 10
- Agent: Thank you for providing those details. Let me ask a few clarifying questions to better understand your situation and determine the appropriate level of care....
- Intent: None (confidence: 0.20)
- Page: Summary

**Turn 4:**
- User: No falls yet but I feel unsteady
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_dizziness (confidence: 0.97)
- Page: Summary

**Final Triage:** None

**Final Recommendation:** None

**Status:** ❌ FAILED

**Errors:**
- Turn 1: Missing parameter 'symptom'
- Turn 1: Missing parameter 'trigger'
- Triage mismatch: expected 'medium', got 'None'

---

### Chronic Fatigue - Medium Urgency (test_005)

**Description:** Patient with persistent fatigue

**Expected Triage:** medium

**Conversation Flow:**

**Turn 1:**
- User: Been exhausted for a week even after sleeping
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_fatigue (confidence: 1.00)
- Page: Symptom Intake

**Turn 2:**
- User: It's about a 7 - I can barely function
- Agent: Thank you for providing those details. Let me ask a few clarifying questions to better understand your situation and determine the appropriate level of care....
- Intent: None (confidence: 0.20)
- Page: Summary

**Turn 3:**
- User: No fever but I have some body aches
- Agent: Sorry, could you say that again?...
- Intent: None (confidence: 0.20)
- Page: Summary

**Final Triage:** None

**Final Recommendation:** None

**Status:** ❌ FAILED

**Errors:**
- Turn 1: Missing parameter 'symptom'
- Turn 1: Missing parameter 'duration'
- Triage mismatch: expected 'medium', got 'None'

---

### Critical Chest Pain - High Urgency (test_006)

**Description:** Patient with chest pain and associated symptoms

**Expected Triage:** high

**Conversation Flow:**

**Turn 1:**
- User: My chest feels tight and I'm lightheaded
- Agent: Based on your symptoms, I'm evaluating the appropriate level of care you need....
- Intent: symptom_redflag (confidence: 1.00)
- Page: Summary

**Final Triage:** None

**Final Recommendation:** None

**Status:** ❌ FAILED

**Errors:**
- Turn 1: Missing parameter 'symptom'
- Turn 1: Missing parameter 'dizziness'
- Turn 1: Missing parameter 'urgency'
- Triage mismatch: expected 'high', got 'None'

---

### Fallback Handling (test_007)

**Description:** Test fallback behavior with unclear inputs

**Expected Triage:** n/a

**Conversation Flow:**

**Turn 1:**
- User: I don't feel good
- Agent: Sorry, can you say that again?...
- Intent: None (confidence: 0.20)
- Page: Start Page

**Turn 2:**
- User: Just not right
- Agent: One more time?...
- Intent: None (confidence: 0.20)
- Page: Start Page

**Turn 3:**
- User: My head hurts
- Agent: Thank you for that information. To help me better understand your situation, I'll need to ask you a few questions about your symptoms....
- Intent: symptom_headache (confidence: 1.00)
- Page: Symptom Intake

**Final Triage:** None

**Final Recommendation:** None

**Status:** ✅ PASSED

---

### Multiple Escalation Fallback (test_008)

**Description:** Test escalation after multiple fallback attempts

**Expected Triage:** n/a

**Conversation Flow:**

**Turn 1:**
- User: zzzzz
- Agent: Sorry, I didn't get that. Can you rephrase?...
- Intent: None (confidence: 0.20)
- Page: Start Page

**Turn 2:**
- User: asdfgh
- Agent: One more time?...
- Intent: None (confidence: 0.20)
- Page: Start Page

**Turn 3:**
- User: qwerty
- Agent: What was that?...
- Intent: None (confidence: 0.20)
- Page: Start Page

**Final Triage:** None

**Final Recommendation:** None

**Status:** ✅ PASSED

---

