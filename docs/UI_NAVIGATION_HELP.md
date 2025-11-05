# Finding Entry Fulfillment in Dialogflow CX UI

## Step-by-Step Navigation

### 1. Access the Agent
Go to: https://dialogflow.cloud.google.com/cx/projects/ai-agent-health-assistant/locations/us-central1/agents/72d18125-ac71-4c56-8ea0-44bfc7f9b039

### 2. Enter Build Mode
- Click **"Build"** tab in the left sidebar (it has a puzzle piece icon)
- You should see the flow canvas with nodes/pages

### 3. Select the Start Page
- You'll see "Default Start Flow" at the top
- Below it, there's a node/box labeled **"Start"** 
- Click directly on the **"Start"** box/node

### 4. Right Panel Should Appear
When you click the Start page, the **right panel** should show these sections (scroll down to see all):

```
┌─────────────────────────────────┐
│ Start                           │ ← Page name at top
├─────────────────────────────────┤
│ Entry fulfillment               │ ← This is what you need!
│   [+ Add dialogue option]       │
├─────────────────────────────────┤
│ Parameters                      │
├─────────────────────────────────┤
│ Routes                          │
│   [+ Add route]                 │
├─────────────────────────────────┤
│ Event handlers                  │
└─────────────────────────────────┘
```

### 5. If You Don't See the Right Panel
Try these:
- Make sure you clicked ON the page box itself (not around it)
- Click the **"<"** arrow on the right edge of screen to expand the panel
- Refresh the page and try again
- Try a different browser (Chrome works best)

### 6. Add Entry Fulfillment
- Click **"+ Add dialogue option"** under Entry fulfillment
- Select **"Agent says"**
- A text box will appear where you can type the greeting

---

## Common UI Issues

**Issue**: Right panel is collapsed
- **Solution**: Look for a **"<"** or **">"** arrow on the right edge, click to expand

**Issue**: Wrong tab selected
- **Solution**: Make sure you're in **Build** tab, not Test or Manage

**Issue**: Page not selected
- **Solution**: The page box should be highlighted/selected when clicked

**Issue**: Browser compatibility
- **Solution**: Use Chrome or Edge (Firefox sometimes has issues)

---

## Visual Cues You're in the Right Place

✅ Left sidebar shows "Build" highlighted  
✅ You see a flow canvas with connected boxes  
✅ One box is labeled "Start"  
✅ Right panel title shows "Start"  
✅ Right panel has sections for Entry fulfillment, Parameters, Routes  

If you see all these, you're in the right place!

