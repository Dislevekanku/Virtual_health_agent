# 🚀 Quick Start Testing Guide

Quick reference for testing the Virtual Health Assistant frontend.

## Start the Server

```bash
python app.py
```

Server will start at: **http://localhost:5000**

## Quick Test Checklist

### ✅ Basic Functionality (5 minutes)

1. **Open Browser**
   - Navigate to http://localhost:5000
   - ✅ Welcome screen appears

2. **Quick Start Button**
   - Click "Headache" button
   - ✅ Message sends automatically
   - ✅ Assistant responds

3. **Manual Input**
   - Type: "I've been dizzy for two days"
   - Press Enter
   - ✅ Message appears
   - ✅ Assistant responds

4. **Multi-Turn**
   - Answer follow-up questions
   - ✅ Conversation continues smoothly

5. **New Chat**
   - Click "New Chat" button
   - ✅ Welcome screen returns
   - ✅ New session starts

### ✅ UI Elements (2 minutes)

- [ ] Header with logo and title
- [ ] Welcome message
- [ ] 4 quick start buttons
- [ ] Input field at bottom
- [ ] Medical disclaimer
- [ ] Message bubbles (user blue, assistant white)
- [ ] Timestamps on messages
- [ ] Typing indicator

### ✅ Error Handling (2 minutes)

1. **Empty Message**
   - Try sending empty message
   - ✅ Should be prevented

2. **Network Error** (optional)
   - Stop server, try sending
   - ✅ Error message appears

### ✅ Responsive Design (2 minutes)

- [ ] Resize browser window
- [ ] Check mobile view (DevTools)
- [ ] ✅ Layout adapts correctly

## Expected Test Results

### Successful Test
- Server starts without errors
- Frontend loads at http://localhost:5000
- All buttons work
- Messages send and receive
- UI is responsive

### Common Issues

**Server won't start:**
```bash
pip install -r requirements.txt
```

**Credentials error:**
- Check `key.json` exists
- Check `agent_info.json` exists

**Frontend not loading:**
- Check server is running
- Check browser console for errors
- Verify port 5000 is not in use

## Full Testing Guide

For comprehensive testing, see: [FRONTEND_TESTING_GUIDE.md](./FRONTEND_TESTING_GUIDE.md)

---

**Time to complete:** ~10 minutes
**Status:** ✅ Ready for testing

