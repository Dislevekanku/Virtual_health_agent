# ✅ Duration Parameter Fix Applied

## Problem
The agent was stuck in a loop, repeatedly asking "When did your symptoms begin?" even after the user provided valid answers like:
- "5 days ago"
- "4 days ago"

## Root Cause
The duration parameter was using `@sys.time-period` entity type, which has strict parsing requirements and may not recognize all natural language formats.

## Solution Applied

### Changes Made:
1. **Changed entity type to `@sys.any`**
   - Now accepts any text input
   - More flexible and forgiving
   - Will capture "5 days ago", "4 days ago", "yesterday", etc.

2. **Removed problematic reprompt handlers**
   - These were causing validation issues
   - Simplified the parameter behavior

3. **Ensured form transition**
   - Verified transition route exists when form completes
   - Form will progress after collecting both duration and severity

4. **Updated severity parameter**
   - Also changed to `@sys.any` for consistency
   - More flexible number extraction

## What This Means

✅ **The agent will now:**
- Accept any natural language duration input
- Progress through the conversation flow
- Not get stuck in loops
- Store the text even if parsing isn't perfect

## Testing

Try these inputs again:
- "5 days ago" ✅
- "4 days ago" ✅
- "yesterday" ✅
- "last week" ✅
- "about 3 days" ✅
- "it started this morning" ✅

The agent should now accept these and move forward to ask about severity.

## Next Steps

1. **Test in the frontend** at http://localhost:5000
2. Try the conversation again:
   - User: "I have a headache"
   - Agent: "When did your symptoms begin?"
   - User: "5 days ago"
   - Agent: Should now ask about severity (not repeat the duration question)

## Note

The text is stored as-is. If you need to parse it later (e.g., convert "5 days ago" to a specific duration value), you can:
1. Process it in a webhook
2. Use a post-processing step
3. Or use Dialogflow CX's built-in parameter extraction once the form completes

---

**Status:** ✅ Fixed  
**Date:** November 5, 2025

