# 🧪 Frontend Testing Guide

Comprehensive testing guide for the Virtual Health Assistant frontend interface.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Starting the Frontend](#starting-the-frontend)
3. [Test Scenarios](#test-scenarios)
4. [UI Component Testing](#ui-component-testing)
5. [Functional Testing](#functional-testing)
6. [Error Handling Testing](#error-handling-testing)
7. [Browser Compatibility](#browser-compatibility)
8. [Performance Testing](#performance-testing)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Files
- ✅ `key.json` - Google Cloud service account credentials
- ✅ `agent_info.json` - Dialogflow CX agent configuration
- ✅ Python 3.8+ installed
- ✅ Dependencies installed: `pip install -r requirements.txt`

### Verify Setup
```bash
# Check Python version
python --version

# Verify dependencies
pip list | grep -E "flask|dialogflow"

# Check configuration files exist
ls key.json agent_info.json
```

---

## Starting the Frontend

### Step 1: Start the Server

**Option A: Direct Python**
```bash
python app.py
```

**Option B: PowerShell Script (Windows)**
```powershell
.\scripts\start_frontend.ps1
```

### Step 2: Verify Server is Running

You should see:
```
============================================================
Virtual Health Assistant - Frontend Server
============================================================
Agent: projects/.../locations/.../agents/...
Location: us-central1

Starting server on http://localhost:5000
Press Ctrl+C to stop
============================================================
```

### Step 3: Open Browser

Navigate to: **http://localhost:5000**

---

## Test Scenarios

### Scenario 1: Initial Load & Welcome Screen

**Test Steps:**
1. Open `http://localhost:5000` in browser
2. Wait for page to load

**Expected Results:**
- ✅ Welcome screen is displayed
- ✅ Header shows "Virtual Health Assistant" with logo
- ✅ Welcome message: "I'm here to help you describe your symptoms..."
- ✅ Four quick start buttons visible:
  - Headache
  - Nausea
  - Dizziness
  - Fatigue
- ✅ Input area at bottom with placeholder text
- ✅ Medical disclaimer visible: "This assistant provides triage recommendations only..."
- ✅ "New Chat" button visible in header (disabled/not needed initially)

**Screenshot Checklist:**
- [ ] Welcome screen layout
- [ ] Quick start buttons styling
- [ ] Input area placement

---

### Scenario 2: Quick Start Button Interaction

**Test Steps:**
1. Click "Headache" quick start button
2. Observe behavior

**Expected Results:**
- ✅ Button click populates input field with "I have a headache"
- ✅ Message is automatically sent
- ✅ Welcome screen hides
- ✅ Chat interface appears
- ✅ User message bubble shows "I have a headache"
- ✅ Typing indicator appears ("Assistant is typing...")
- ✅ Assistant response appears after a few seconds
- ✅ Response is formatted correctly with line breaks

**Repeat for:**
- [ ] Nausea button
- [ ] Dizziness button
- [ ] Fatigue button

---

### Scenario 3: Manual Message Input

**Test Steps:**
1. Type a message in the input field: "I've been dizzy for two days"
2. Press Enter or click Send button

**Expected Results:**
- ✅ Message appears in chat as user message
- ✅ Input field clears
- ✅ Typing indicator shows
- ✅ Assistant responds appropriately
- ✅ Timestamp appears on each message
- ✅ Messages scroll to bottom automatically

**Test Variations:**
- [ ] Send with Enter key
- [ ] Send with Send button click
- [ ] Send with Shift+Enter (should create new line, not send)
- [ ] Send empty message (should be prevented)
- [ ] Send very long message (should wrap correctly)

---

### Scenario 4: Multi-Turn Conversation

**Test Steps:**
1. Send: "I have a headache"
2. Wait for assistant response
3. Respond to follow-up questions
4. Continue conversation for 3-5 turns

**Expected Results:**
- ✅ Each message appears in correct order
- ✅ User messages on right (blue), assistant on left (white)
- ✅ Conversation context is maintained
- ✅ Follow-up questions are relevant
- ✅ Session ID persists throughout conversation

**Test Messages:**
```
User: "I have a headache"
AI: [Asks about duration/severity]
User: "It started yesterday"
AI: [Asks about severity]
User: "About a 4 out of 10"
AI: [Provides triage recommendation]
```

---

### Scenario 5: Session Management

**Test Steps:**
1. Start a conversation
2. Send 2-3 messages
3. Click "New Chat" button in header
4. Verify new session starts

**Expected Results:**
- ✅ "New Chat" button is clickable
- ✅ Clicking clears current conversation
- ✅ Welcome screen reappears
- ✅ New session ID is created
- ✅ Previous conversation is saved to history (check localStorage or `/api/conversation/history`)

---

### Scenario 6: Input Field Behavior

**Test Steps:**
1. Type a short message
2. Type a longer message (multiple lines)
3. Test auto-resize

**Expected Results:**
- ✅ Input field auto-resizes for multi-line text
- ✅ Maximum height is capped (around 120px)
- ✅ Scrollbar appears if content exceeds max height
- ✅ Placeholder text disappears when typing
- ✅ Text wraps correctly

---

### Scenario 7: Typing Indicator

**Test Steps:**
1. Send a message
2. Observe typing indicator

**Expected Results:**
- ✅ Typing indicator appears immediately after sending
- ✅ Shows animated dots (three dots bouncing)
- ✅ Text says "Assistant is typing..."
- ✅ Indicator disappears when response arrives
- ✅ Indicator is positioned at bottom of messages

---

### Scenario 8: Error Handling

**Test Scenarios:**

**A. Network Error Simulation**
1. Stop the backend server
2. Try to send a message
3. Observe error handling

**Expected Results:**
- ✅ Error message appears: "Network error. Please check your connection and try again."
- ✅ Error message is styled differently (red/error styling)
- ✅ Error message auto-dismisses after 5 seconds
- ✅ Input field re-enables after error

**B. Invalid Response**
1. Send a message that causes backend error
2. Observe error handling

**Expected Results:**
- ✅ Error message from backend is displayed
- ✅ User can retry sending message
- ✅ UI remains functional

---

### Scenario 9: Responsive Design

**Test Steps:**
1. Open in desktop browser (1920x1080)
2. Resize to tablet size (768x1024)
3. Resize to mobile size (375x667)
4. Test on actual mobile device (optional)

**Expected Results:**
- ✅ Layout adapts to screen size
- ✅ Text remains readable
- ✅ Buttons are appropriately sized for touch
- ✅ Input area is accessible
- ✅ Messages wrap correctly
- ✅ No horizontal scrolling

**Breakpoints to Test:**
- [ ] Desktop (>1024px)
- [ ] Tablet (768px - 1024px)
- [ ] Mobile (<768px)

---

### Scenario 10: Conversation History

**Test Steps:**
1. Complete a full conversation
2. Check browser console for localStorage
3. Check `/api/conversation/history` endpoint

**Expected Results:**
- ✅ Conversation saved to localStorage
- ✅ Conversation saved to server (if endpoint called)
- ✅ History includes:
  - Session ID
  - Timestamp
  - All messages (user + assistant)
  - Summary (if available)

**Verify:**
```javascript
// In browser console
JSON.parse(localStorage.getItem('conversationHistory'))
```

---

## UI Component Testing

### Header Component
- [ ] Logo displays correctly
- [ ] Title "Virtual Health Assistant" is visible
- [ ] "New Chat" button is functional
- [ ] Header is sticky/fixed at top

### Welcome Screen
- [ ] Icon displays correctly
- [ ] Welcome message is readable
- [ ] Quick start buttons are clickable
- [ ] Layout is centered and balanced

### Message Bubbles
- [ ] User messages: Blue background, right-aligned
- [ ] Assistant messages: White background, left-aligned
- [ ] Avatars show "You" and "AI"
- [ ] Timestamps are formatted correctly (HH:MM)
- [ ] Long messages wrap properly
- [ ] Line breaks in messages are preserved

### Input Area
- [ ] Placeholder text is visible
- [ ] Send button is always visible
- [ ] Input field is accessible
- [ ] Medical disclaimer is visible
- [ ] Input area is fixed at bottom

### Typing Indicator
- [ ] Animation is smooth
- [ ] Positioned correctly
- [ ] Text is readable
- [ ] Disappears when response arrives

---

## Functional Testing

### API Endpoints

**1. Health Check**
```bash
curl http://localhost:5000/api/health
```
**Expected:** `{"status": "healthy", "agent": "...", "active_sessions": 0}`

**2. Create Session**
```bash
curl -X POST http://localhost:5000/api/session/new
```
**Expected:** `{"success": true, "session_id": "..."}`

**3. Send Message**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache", "session_id": "test-123"}'
```
**Expected:** `{"success": true, "session_id": "...", "response": "...", ...}`

**4. Get History**
```bash
curl http://localhost:5000/api/conversation/history
```
**Expected:** `{"success": true, "conversations": [...]}`

---

## Error Handling Testing

### Test Cases

1. **Empty Message**
   - Try to send empty message
   - Should be prevented or show error

2. **Server Not Running**
   - Stop server, try to send message
   - Should show network error

3. **Invalid Session ID**
   - Send message with invalid session_id
   - Should create new session automatically

4. **Backend Error**
   - Cause backend error (e.g., invalid credentials)
   - Should display error message gracefully

5. **Slow Network**
   - Throttle network in DevTools
   - Should show typing indicator until response

---

## Browser Compatibility

Test in the following browsers:

- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (latest)
- [ ] **Edge** (latest)
- [ ] **Mobile Chrome** (Android)
- [ ] **Mobile Safari** (iOS)

**Key Checks:**
- [ ] CSS styles render correctly
- [ ] JavaScript functions work
- [ ] Fetch API works
- [ ] LocalStorage works
- [ ] Responsive design works

---

## Performance Testing

### Load Time
- [ ] Initial page load < 2 seconds
- [ ] CSS loads quickly
- [ ] JavaScript executes without blocking

### Message Response
- [ ] Typing indicator appears < 100ms
- [ ] Response time < 5 seconds (depends on Dialogflow)
- [ ] No UI freezing during API calls

### Memory Usage
- [ ] No memory leaks after multiple conversations
- [ ] LocalStorage doesn't grow unbounded (max 50 conversations)

### Network
- [ ] API calls are efficient
- [ ] No unnecessary requests
- [ ] Error retries are reasonable

---

## Troubleshooting

### Common Issues

**1. Server Won't Start**
```
Error: ModuleNotFoundError: No module named 'flask'
```
**Solution:** `pip install -r requirements.txt`

**2. Credentials Error**
```
Error: Could not load credentials
```
**Solution:** Verify `key.json` exists and is valid

**3. Agent Not Found**
```
Error: Agent not found
```
**Solution:** Check `agent_info.json` has correct agent_name

**4. CORS Errors**
```
Error: CORS policy blocked
```
**Solution:** Verify `CORS(app)` is enabled in `app.py`

**5. Messages Not Sending**
```
Error: Network error
```
**Solution:** 
- Check server is running
- Check browser console for errors
- Verify API endpoint is correct

**6. Styling Issues**
```
CSS not loading
```
**Solution:** 
- Check `static/style.css` exists
- Verify Flask static folder configuration
- Clear browser cache

---

## Test Checklist Summary

### Initial Setup
- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] Frontend loads at http://localhost:5000

### Welcome Screen
- [ ] All elements visible
- [ ] Quick start buttons work
- [ ] Layout is correct

### Chat Functionality
- [ ] Messages send successfully
- [ ] Responses appear correctly
- [ ] Multi-turn conversations work
- [ ] Session persists

### UI/UX
- [ ] Responsive design works
- [ ] Typing indicator shows
- [ ] Error messages display
- [ ] Input field behaves correctly

### Advanced Features
- [ ] New chat button works
- [ ] Conversation history saves
- [ ] Session management works
- [ ] Error handling is graceful

---

## Reporting Issues

When reporting issues, include:

1. **Browser & Version:** e.g., Chrome 120.0
2. **OS:** e.g., Windows 11
3. **Steps to Reproduce:** Detailed steps
4. **Expected Behavior:** What should happen
5. **Actual Behavior:** What actually happened
6. **Console Errors:** Any JavaScript errors
7. **Network Tab:** Failed API requests
8. **Screenshots:** Visual evidence

---

## Next Steps

After completing basic testing:

1. **Integration Testing:** Test with real Dialogflow CX agent
2. **End-to-End Testing:** Complete user journeys
3. **Accessibility Testing:** WCAG compliance
4. **Security Testing:** Input validation, XSS prevention
5. **Load Testing:** Multiple concurrent users

---

**Last Updated:** 2025-01-15
**Version:** 1.0

