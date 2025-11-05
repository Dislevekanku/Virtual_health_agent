# Troubleshooting Guide

Common issues and solutions for the Virtual Health Assistant.

## Setup Issues

### Service Account Key Not Found

**Error**: `FileNotFoundError: key.json`

**Solution**:
1. Download service account key from GCP Console
2. Save as `key.json` in project root
3. Verify file permissions

### Agent Info Not Found

**Error**: `FileNotFoundError: agent_info.json`

**Solution**:
1. Create `agent_info.json` with your agent details:
```json
{
  "project_id": "your-project-id",
  "location": "us-central1",
  "agent_id": "your-agent-id"
}
```

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
```

## Agent Issues

### Agent Not Responding

**Symptoms**: No response from agent

**Solutions**:
1. Check agent is active in Dialogflow CX Console
2. Verify agent ID in `agent_info.json`
3. Check service account has Dialogflow CX permissions
4. Review Cloud Logging for errors

### Intent Not Matching

**Symptoms**: Agent doesn't recognize user input

**Solutions**:
1. Add more training phrases to intents
2. Lower classification threshold (in agent settings)
3. Check intent route configuration
4. Review NLU settings

### Parameter Extraction Failing

**Symptoms**: Parameters not being collected

**Solutions**:
1. Verify form parameters are configured
2. Check entity types match input
3. Review parameter prompts
4. Test with simpler inputs

## Frontend Issues

### Frontend Not Loading

**Error**: Connection refused or 404

**Solutions**:
1. Ensure Flask app is running: `python app.py`
2. Check port 5000 is available
3. Verify `templates/` and `static/` directories exist
4. Check browser console for errors

### Messages Not Displaying

**Symptoms**: Messages not appearing in chat

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify API endpoint is accessible
3. Check network tab for failed requests
4. Review Flask logs for errors

### Session Issues

**Symptoms**: Session not persisting

**Solutions**:
1. Check session ID is being generated
2. Verify session storage in Flask
3. Clear browser cache and cookies
4. Check CORS settings

## Webhook Issues

### Webhook Not Called

**Symptoms**: Webhook not being invoked

**Solutions**:
1. Verify webhook URL in Dialogflow CX
2. Check Cloud Function is deployed
3. Verify webhook is enabled on page
4. Check IAM permissions

### Webhook Errors

**Error**: 500 Internal Server Error

**Solutions**:
1. Check Cloud Function logs
2. Verify datastore access (if using RAG)
3. Review webhook code for errors
4. Check service account permissions

### Datastore Not Found

**Error**: Datastore not accessible

**Solutions**:
1. Verify datastore exists in Vertex AI Search
2. Check datastore ID matches configuration
3. Verify service account has Discovery Engine permissions
4. Review datastore status in console

## Deployment Issues

### Cloud Function Deployment Fails

**Error**: Deployment error

**Solutions**:
1. Check function code for syntax errors
2. Verify entry point is correct
3. Check dependencies in `requirements_webhook.txt`
4. Review deployment logs

### CORS Issues

**Error**: CORS policy blocked

**Solutions**:
1. Enable CORS in Flask app
2. Configure allowed origins
3. Check preflight requests
4. Review CORS headers

## Parameter Issues

### Parameters Not Substituting

**Symptoms**: `{parameter}` showing instead of values

**Solutions**:
1. Use Dialogflow syntax: `$session.params.parameter`
2. Verify parameter is set before use
3. Check parameter name spelling
4. Review parameter scope

### Duplicate Messages

**Symptoms**: Multiple messages appearing

**Solutions**:
1. Remove duplicate entry fulfillments
2. Ensure single message per page
3. Check transition route messages
4. Review webhook responses

## Testing Issues

### Tests Failing

**Error**: Test failures

**Solutions**:
1. Verify agent is configured correctly
2. Check test scenarios match agent setup
3. Review test logs
4. Update test scenarios if needed

## Getting Help

1. Check logs:
   - Flask: Console output
   - Cloud Function: Cloud Logging
   - Dialogflow: Agent logs

2. Review documentation:
   - [Setup Guide](SETUP_GUIDE.md)
   - [API Reference](API_REFERENCE.md)

3. Common solutions:
   - Restart Flask app
   - Redeploy Cloud Function
   - Clear browser cache
   - Check GCP quotas

4. If issues persist:
   - Review error messages carefully
   - Check Cloud Logging
   - Verify all configuration files
   - Test with minimal setup

