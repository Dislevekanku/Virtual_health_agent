# 🎯 Agent Builder Grounding Integration Guide

## **Overview**
Integrate Vertex AI Search datastore directly into Agent Builder as a grounding tool. This allows the agent to automatically search clinical guidelines and use retrieved content when composing replies.

## **Method 1: Direct Datastore Integration (Recommended)**

### **Step 1: Open Agent Builder**
1. **Go to Vertex AI Agent Builder**: https://console.cloud.google.com/vertex-ai/agent-builder
2. **Select your project**: `ai-agent-health-assistant`
3. **Open your agent** (or create a new one)

### **Step 2: Add Datastore Integration**
1. **Navigate to Tools/Integrations**:
   - Click on **"Tools"** or **"Integrations"** tab
   - Look for **"Datastores"** or **"Grounding"** section

2. **Add Vertex AI Search Datastore**:
   - Click **"+ Add Datastore"** or **"+ Connect Datastore"**
   - Select **"Vertex AI Search"**
   - Choose your datastore: `dfci-clinical-guidelines` or `clinical-guidelines-datastore`
   - Click **"Connect"** or **"Add"**

### **Step 3: Configure Grounding Settings**
1. **Enable Grounding**:
   - Go to **Agent Configuration** or **Settings**
   - Find **"Grounding"** or **"Knowledge Base"** section
   - Enable **"Use datastore for grounding"**
   - Select your connected datastore

2. **Configure Search Parameters**:
   - **Max results**: 5-10
   - **Relevance threshold**: 0.7
   - **Enable citations**: Yes
   - **Search mode**: Hybrid (semantic + keyword)

### **Step 4: Test Integration**
1. **Go to Preview/Test section**
2. **Test queries**:
   ```
   What are red flag headache symptoms?
   When should someone with nausea see a doctor?
   What is orthostatic hypotension?
   ```
3. **Expected behavior**:
   - Agent automatically searches datastore
   - Uses retrieved content in responses
   - Includes citations with document IDs

## **Method 2: Custom Grounding Function (If Direct Integration Not Available)**

If Agent Builder UI doesn't have direct datastore integration, create a custom grounding function.

### **Step 1: Create Grounding Cloud Function**
```python
def ground_and_generate(user_text):
    """
    Performs search + model generation
    Called by Agent Builder as external tool
    """
    # 1. Search clinical guidelines
    search_results = search_clinical_guidelines(user_text)
    
    # 2. Generate response with retrieved content
    response = generate_with_context(user_text, search_results)
    
    return response
```

### **Step 2: Deploy Grounding Function**
```bash
gcloud functions deploy grounding-tool \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --source . \
  --entry-point ground_and_generate \
  --region us-central1
```

### **Step 3: Configure Agent Builder**
1. **Add External Tool**:
   - Go to **Tools** → **External Tools**
   - Add your grounding function URL
   - Configure tool parameters

2. **Add to Agent Flow**:
   - In dialog nodes, add step to invoke grounding tool
   - Use retrieved content when composing replies

## **Method 3: Agent Development Kit (ADK) Integration**

### **Step 1: Install ADK**
```bash
pip install google-cloud-aiplatform[adk]
```

### **Step 2: Create Agent with Grounding**
```python
from google.cloud import aiplatform
from google.cloud.aiplatform.adk import Agent, VertexAiSearchTool

# Create agent with grounding tool
agent = Agent(
    name="clinical-assistant",
    description="Clinical decision support agent",
    grounding_tools=[
        VertexAiSearchTool(
            datastore_id="clinical-guidelines-datastore",
            project_id="ai-agent-health-assistant"
        )
    ]
)

# Deploy agent
agent.deploy()
```

## **Implementation Details**

### **Search Tool Configuration**
```python
search_tool = {
    "name": "clinical_guidelines_search",
    "description": "Search clinical guidelines for evidence-based information",
    "parameters": {
        "query": {
            "type": "string",
            "description": "Medical query or symptom description"
        }
    },
    "datastore": "clinical-guidelines-datastore",
    "max_results": 5,
    "relevance_threshold": 0.7
}
```

### **Agent Flow Configuration**
```python
flow_config = {
    "start_page": {
        "entry_fulfillment": {
            "grounding_tools": ["clinical_guidelines_search"],
            "grounding_settings": {
                "enable_citations": True,
                "citation_format": "numbered",
                "include_confidence": True
            }
        }
    }
}
```

## **Testing and Validation**

### **Test Scenarios**
1. **Red Flag Detection**:
   ```
   Query: "What are red flag headache symptoms?"
   Expected: Thunderclap headache, vision changes, emergency warnings
   ```

2. **Triage Assessment**:
   ```
   Query: "When should I see a doctor for nausea?"
   Expected: Persistent vomiting criteria, urgency levels
   ```

3. **Clinical Definitions**:
   ```
   Query: "What is orthostatic hypotension?"
   Expected: BP drop definition, symptoms, management
   ```

### **Success Criteria**
- ✅ Agent automatically searches datastore
- ✅ Responses include clinical guidelines content
- ✅ Citations with document IDs are provided
- ✅ Emergency symptoms are flagged appropriately
- ✅ Triage recommendations are included

## **Troubleshooting**

### **Common Issues**
1. **Datastore not found**:
   - Verify datastore exists in Vertex AI Search
   - Check project permissions
   - Ensure datastore is in correct region

2. **No search results**:
   - Check datastore content
   - Verify search queries are appropriate
   - Adjust relevance threshold

3. **Integration not working**:
   - Check Agent Builder UI for grounding options
   - Verify tool configuration
   - Test with simple queries first

### **Alternative Approaches**
If direct integration fails:
1. Use custom grounding function
2. Implement via ADK
3. Use webhook-based integration (previous method)

## **Best Practices**

### **Grounding Configuration**
- **Max results**: 5-10 for optimal context
- **Relevance threshold**: 0.7 for medical accuracy
- **Citation format**: Numbered for clarity
- **Search mode**: Hybrid for comprehensive results

### **Agent Behavior**
- **Automatic grounding**: Enable for all medical queries
- **Fallback handling**: Graceful degradation when no results
- **Safety checks**: Always include medical disclaimers
- **Response format**: Evidence-based with citations

## **Next Steps**

1. **Choose integration method** based on available UI
2. **Configure grounding settings** for optimal performance
3. **Test with medical queries** to validate functionality
4. **Monitor performance** and adjust parameters as needed
5. **Deploy to production** when satisfied with results

---

**This integration provides direct grounding capabilities within Agent Builder, making it the most efficient approach for clinical decision support.** 🎯
