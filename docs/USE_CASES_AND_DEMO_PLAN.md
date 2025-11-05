# Use Cases and Demo Plan

## ✅ Confirmed Use Cases

The Virtual Health Assistant supports the following four symptom categories:

### 1. **Headache** 
- **Intent**: `symptom_headache`
- **Training Phrases**: 8+ examples including variations like "I have a headache", "My head hurts really bad", "Headache started this morning"
- **Red Flag Detection**: `symptom_headache_redflag` intent for urgent cases (vision changes, worst headache of life, neurological deficits)
- **Triage Levels**: 
  - High: Thunderclap headache, vision changes, fever + neck stiffness
  - Medium: Progressively worsening, severity 7-8/10
  - Low: Mild-moderate, responsive to OTC meds

### 2. **Nausea**
- **Intent**: `symptom_nausea`
- **Training Phrases**: 7+ examples including "Feeling nauseous since last night", "Can't keep food down"
- **Red Flag Detection**: Hematemesis (vomiting blood), severe dehydration, bilious vomiting
- **Triage Levels**:
  - High: Vomiting blood, severe dehydration, severe abdominal pain
  - Medium: Persistent vomiting >24 hours, unable to tolerate fluids 12+ hours
  - Low: Mild nausea, tolerating fluids

### 3. **Dizziness**
- **Intent**: `symptom_dizziness`
- **Training Phrases**: 6+ examples including "I get dizzy when I stand up quickly", "The room is spinning"
- **Red Flag Detection**: BEFAST stroke signs, chest pain, loss of consciousness
- **Triage Levels**:
  - High: Stroke signs, chest pain/SOB, sudden severe vertigo
  - Medium: New onset with vomiting, orthostatic with near-syncope
  - Low: Mild intermittent dizziness, known BPPV recurrence

### 4. **Fatigue**
- **Intent**: `symptom_fatigue`
- **Training Phrases**: 6+ examples including "Been exhausted for a week even after sleeping", "I'm so tired all the time"
- **Red Flag Detection**: Chest pain + SOB, altered mental status, significant weight loss
- **Triage Levels**:
  - High: Chest pain + SOB, altered mental status, jaundice
  - Medium: Persistent >4 weeks, interfering with work/daily activities
  - Low: Mild-moderate <4 weeks, improving trend

---

## 🎯 Demo Selection (2-3 Use Cases)

For the demonstration, we recommend focusing on **2-3 use cases** that showcase the full range of triage capabilities:

### **Recommended Demo Scenarios:**

#### **Demo 1: Headache (High Urgency - Red Flag)** ⭐ **PRIMARY**
- **Scenario**: "I've had a headache for two days and now my vision is blurry"
- **Why**: 
  - Shows red flag detection working correctly
  - Demonstrates immediate escalation to emergency care
  - Clear clinical urgency example
  - Most common symptom type
- **Expected Flow**:
  1. Intent recognition: `symptom_headache_redflag`
  2. Immediate triage to HIGH urgency
  3. Recommendation: Emergency department or call 911
  4. Proper citation from clinical guidelines (OID-HEADACHE-001)

#### **Demo 2: Nausea (Medium Urgency - Routine Triage)** ⭐ **SECONDARY**
- **Scenario**: "I've been feeling nauseous for 3 days, can't keep much food down but I'm still drinking water"
- **Why**:
  - Shows routine triage logic working
  - Demonstrates clarifying questions
  - Shows same-week appointment recommendation
  - Common GI complaint
- **Expected Flow**:
  1. Intent recognition: `symptom_nausea`
  2. Parameter collection: duration, severity, hydration status
  3. Clarifying questions about vomiting frequency
  4. Triage to MEDIUM urgency
  5. Recommendation: Same-week appointment with PCP

#### **Demo 3: Fatigue (Low Urgency - Self-Care)** ⭐ **OPTIONAL**
- **Scenario**: "I've been really tired for about a week, probably from working late hours"
- **Why**:
  - Shows self-care pathway
  - Demonstrates low-urgency triage
  - Shows follow-up recommendations
  - Common complaint with broad differential
- **Expected Flow**:
  1. Intent recognition: `symptom_fatigue`
  2. Parameter collection: duration, severity, functional impact
  3. Clarifying questions about sleep, stressors
  4. Triage to LOW urgency
  5. Recommendation: Self-care, monitor, follow up if persists

---

## 📊 Demo Priority Matrix

| Use Case | Urgency Level | Complexity | Demo Priority | Notes |
|----------|--------------|------------|---------------|-------|
| Headache (Red Flag) | High | Medium | ⭐⭐⭐ **PRIMARY** | Shows emergency escalation |
| Nausea (Medium) | Medium | High | ⭐⭐ **SECONDARY** | Shows routine triage logic |
| Fatigue (Low) | Low | Medium | ⭐ **OPTIONAL** | Shows self-care pathway |
| Dizziness | Various | High | 🔄 **Backup** | Can substitute for Nausea if needed |

---

## 🎬 Demo Script Recommendations

### **Minimum Demo (2 scenarios - ~10 minutes):**
1. **Headache with Red Flag** (5 min) - Emergency escalation
2. **Nausea Routine** (5 min) - Standard triage workflow

### **Full Demo (3 scenarios - ~15 minutes):**
1. **Headache with Red Flag** (5 min) - Emergency escalation
2. **Nausea Routine** (5 min) - Standard triage workflow  
3. **Fatigue Self-Care** (5 min) - Low-urgency pathway

---

## ✅ Verification Checklist

- [x] All 4 use cases are implemented in the agent
- [x] Training phrases are defined for each intent
- [x] Red flag detection is configured
- [x] Triage logic supports High/Medium/Low urgency
- [x] Clinical guidelines are available in Vertex AI Search
- [x] Agent can cite sources (document IDs)
- [ ] **Demo scenarios tested end-to-end** (Next step)
- [ ] **Test results documented** (Next step)

---

**Last Updated**: October 2025  
**Status**: Use cases confirmed, demo scenarios defined
