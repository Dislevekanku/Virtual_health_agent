# 🏥 Virtual Health Assistant - Frontend

A modern, responsive web interface for interacting with the Dialogflow CX Virtual Health Assistant agent.

## ✨ Features

- 💬 Real-time chat interface
- 🎨 Modern, medical-appropriate UI design
- 📱 Fully responsive (mobile-friendly)
- 🔄 Session management
- ⚡ Typing indicators
- 🎯 Quick start buttons for common symptoms
- 🔒 Secure backend API (credentials stay on server)

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Service account key** (`key.json`) in the project root
3. **Agent info** (`agent_info.json`) configured

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5000
   ```

That's it! The frontend will automatically connect to your Dialogflow CX agent.

---

## 📁 Project Structure

```
.
├── app.py                 # Flask backend server
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   ├── style.css         # CSS styles
│   └── script.js         # Frontend JavaScript
├── key.json              # Service account credentials
├── agent_info.json       # Agent configuration
└── requirements.txt      # Python dependencies
```

---

## 🎨 UI Features

### Welcome Screen
- Professional greeting
- Quick start buttons for common symptoms (Headache, Nausea, Dizziness, Fatigue)
- Clear instructions

### Chat Interface
- Clean, medical-appropriate design
- User messages (blue) vs Assistant messages (white)
- Timestamps for each message
- Smooth animations

### Input Area
- Auto-resizing textarea
- Send button with icon
- Medical disclaimer footer
- Enter to send, Shift+Enter for new line

---

## 🔧 Configuration

### Agent Settings

The agent configuration is loaded from `agent_info.json`:
```json
{
  "agent_name": "projects/.../agents/...",
  "display_name": "Virtual-Health-Assistant-POC",
  "project_id": "ai-agent-health-assistant",
  "location": "us-central1"
}
```

### Server Settings

Default server runs on `http://localhost:5000`. To change:

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## 🔌 API Endpoints

### `POST /api/chat`
Send a message to the agent.

**Request:**
```json
{
  "message": "I have a headache",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid",
  "response": "Agent response text",
  "intent": "symptom_headache",
  "confidence": 0.95,
  "current_page": "Symptom Intake",
  "parameters": {}
}
```

### `POST /api/session/new`
Create a new chat session.

**Response:**
```json
{
  "success": true,
  "session_id": "uuid"
}
```

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "projects/.../agents/...",
  "active_sessions": 5
}
```

---

## 🛠️ Development

### Running in Debug Mode

The server runs in debug mode by default. This enables:
- Auto-reload on code changes
- Detailed error messages
- Development tools

### Customizing the UI

**Colors:** Edit CSS variables in `static/style.css`:
```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #10b981;
    /* ... */
}
```

**Welcome Message:** Edit `templates/index.html`:
```html
<h2>Welcome to Virtual Health Assistant</h2>
<p>Your custom message here...</p>
```

**Quick Start Buttons:** Edit `templates/index.html`:
```html
<button class="quick-start-btn" data-message="Your message">Button Text</button>
```

---

## 🐛 Troubleshooting

### "Connection Error"
- Check that `key.json` exists and is valid
- Verify `agent_info.json` has correct agent name
- Ensure Dialogflow CX API is enabled in GCP

### "Failed to get response"
- Check server logs in terminal
- Verify agent is deployed and accessible
- Check network connectivity

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Use different port
```

---

## 📱 Mobile Support

The frontend is fully responsive and works on:
- 📱 Mobile phones (iOS, Android)
- 📲 Tablets
- 💻 Desktop browsers
- 🖥️ Large screens

---

## 🔒 Security Notes

- **Credentials stay on server**: The `key.json` file is never sent to the browser
- **Session management**: Each conversation has a unique session ID
- **CORS enabled**: For development (disable in production if needed)

### Production Deployment

For production:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure HTTPS
4. Set up proper session storage (Redis/database)
5. Add authentication/authorization
6. Disable CORS or configure allowed origins

---

## 📝 Example Usage

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open browser:** `http://localhost:5000`

3. **Start chatting:**
   - Click a quick start button, OR
   - Type your message and press Enter

4. **Example conversation:**
   ```
   User: I have a headache
   Assistant: Thank you for that information. To help me better understand...
   
   User: It started this morning
   Assistant: On a scale of 0 to 10, how would you rate your symptoms?
   
   User: About a 3
   Assistant: Based on your symptoms, this may improve with rest...
   ```

---

## 🎯 Next Steps

- [ ] Add authentication for user tracking
- [ ] Implement conversation history storage
- [ ] Add export conversation feature
- [ ] Integrate with EHR systems
- [ ] Add voice input support
- [ ] Implement multi-language support

---

## 📞 Support

For issues or questions:
1. Check server logs in terminal
2. Verify agent configuration
3. Test agent directly in Dialogflow CX console
4. Review API responses in browser DevTools

---

**Last Updated:** November 4, 2025  
**Version:** 1.0.0

