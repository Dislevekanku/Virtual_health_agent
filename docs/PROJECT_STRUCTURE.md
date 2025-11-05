# Project Structure

This document describes the organization of the Virtual Health Assistant project.

## Directory Structure

```
.
├── app.py                      # Flask backend server (main entry point)
├── main.py                     # Cloud Function entry point for webhook
├── rag_simplified.py           # RAG pipeline and webhook implementation
├── requirements.txt            # Python dependencies
├── requirements_webhook.txt    # Webhook-specific dependencies
│
├── static/                     # Frontend static files
│   ├── style.css               # Frontend styles
│   └── script.js               # Frontend JavaScript
│
├── templates/                   # HTML templates
│   └── index.html              # Main chat interface
│
├── scripts/                     # Setup and utility scripts
│   ├── create_agent.py         # Agent creation script
│   ├── create_flows.py         # Flow creation script
│   ├── test_agent.py           # Agent testing script
│   └── *.py                    # Other utility scripts
│
├── docs/                        # Documentation
│   ├── QUICK_START.md          # Quick start guide
│   ├── SETUP_GUIDE.md          # Complete setup guide
│   ├── API_REFERENCE.md        # API documentation
│   └── *.md                    # Other documentation files
│
├── tests/                       # Test files
│   ├── test_agent.py           # Main test script
│   ├── test_scenarios.json     # Test scenarios
│   └── test_results.json      # Test results
│
├── config/                      # Configuration templates
│   ├── conversation_flow.json  # Flow configuration template
│   ├── response_templates.json # Response templates
│   └── training_examples.json # Training examples
│
├── guidelines/                  # Clinical guidelines (optional)
│   └── *.txt                   # Guideline files
│
├── .gitignore                   # Git ignore rules
├── .gitattributes              # Git attributes
├── README.md                   # Main project documentation
├── LICENSE                     # MIT License
├── CONTRIBUTING.md             # Contribution guidelines
└── CHANGELOG.md                # Change log
```

## Core Files

### Backend
- **app.py**: Flask application serving the frontend and API endpoints
- **main.py**: Cloud Function entry point for webhook deployment
- **rag_simplified.py**: RAG pipeline implementation for clinical guidelines

### Frontend
- **templates/index.html**: Main chat interface HTML
- **static/style.css**: Frontend styling
- **static/script.js**: Frontend JavaScript for chat functionality

### Configuration
- **requirements.txt**: Python dependencies for main application
- **requirements_webhook.txt**: Additional dependencies for webhook
- **agent_info.json**: Agent configuration (not in repo, use template)

## Scripts Directory

The `scripts/` directory contains utility scripts for:
- Agent setup and configuration
- Flow creation and modification
- Testing and validation
- Deployment utilities
- One-time fixes and improvements

## Documentation

The `docs/` directory contains:
- Setup guides
- Integration guides
- Troubleshooting documentation
- API references
- Configuration guides

## Tests

The `tests/` directory contains:
- Test scripts
- Test scenarios
- Test results

## Configuration Templates

The `config/` directory contains:
- JSON templates for agent configuration
- Response templates
- Training examples

These are templates - actual configuration should be created from these or stored outside the repo.

## Important Notes

- **Never commit** `key.json` or `agent_info.json` - these contain sensitive credentials
- Use `.gitignore` to exclude sensitive files
- Configuration templates are safe to commit
- Test results are excluded from git by default

