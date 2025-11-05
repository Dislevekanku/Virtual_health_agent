# Quick Start Guide

Get the Virtual Health Assistant up and running in minutes.

## Prerequisites

- Python 3.8+
- Google Cloud Project
- Service account with Dialogflow CX permissions

## Setup Steps

### 1. Clone and Install

```bash
git clone <repository-url>
cd vertex-ai-poc
pip install -r requirements.txt
```

### 2. Configure Credentials

1. Download service account JSON key from GCP Console
2. Save as `key.json` in project root
3. **Never commit this file!**

### 3. Configure Agent

Create `agent_info.json`:
```json
{
  "project_id": "your-project-id",
  "location": "us-central1",
  "agent_id": "your-agent-id"
}
```

### 4. Run Frontend

```bash
python app.py
```

Visit `http://localhost:5000`

## Next Steps

- See [Full Setup Guide](SETUP_GUIDE.md)
- Review [Agent Configuration](AGENT_CONFIG.md)
- Check [Troubleshooting](TROUBLESHOOTING.md)
