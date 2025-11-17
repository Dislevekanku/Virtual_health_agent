# Session Memory & Logging Implementation

## Overview

This document describes the implementation of comprehensive session memory and detailed logging for the Virtual Health Assistant multi-agent pipeline.

## Implementation Summary

### 1. Session Management

#### Enhanced Session Storage

**Structure:**
```python
LOCAL_SESSION_STORE: Dict[str, Dict[str, Any]] = {
    "session_id": {
        "history": [turn_entry, ...],  # Conversation turns
        "agent_outputs": [agent_output, ...],  # All agent outputs
        "total_turns": int  # Turn counter
    }
}
```

**Turn Entry Structure:**
```json
{
    "timestamp": "ISO timestamp",
    "user_input": "user message",
    "response": "assistant response",
    "triage_level": "low|medium|high",
    "urgency_score": 1-10,
    "reasoning": ["reason1", "reason2"],
    "red_flags": ["flag1", ...],
    "intake": {...},
    "critic_score": 0-10,
    "latency_ms": float,
    "agent_outputs": [...]
}
```

**Features:**
- ✅ Multi-turn conversation support
- ✅ Agent outputs stored per turn
- ✅ Session history retrieval
- ✅ Turn counter tracking
- ✅ Firestore integration (when available)
- ✅ Local fallback storage

### 2. Detailed Logging

#### Agent Decision Logging

**`_log_agent_decision()` Function:**
- Logs each agent's output/decision
- Parses JSON outputs when possible
- Structured format for analysis

**Log Structure:**
```json
{
    "log_type": "agent_decision",
    "session_id": "...",
    "agent": "IntakeAgent|ReasoningAgent|DataAgent|...",
    "user_input": "...",
    "output": "...",
    "parsed_output": {...},  // If JSON
    "timestamp": "ISO timestamp"
}
```

**Agents Logged:**
- ✅ IntakeAgent
- ✅ ReasoningAgent
- ✅ DataAgent
- ✅ DraftResponseAgent
- ✅ CriticAgent
- ✅ RefinerAgent
- ✅ FinalResponseAgent

#### Final Response Logging

**`_log_and_persist()` Function:**
- Logs final response with complete context
- Stores to session memory
- Includes all agent outputs

**Log Structure:**
```json
{
    "log_type": "final_response",
    "session_id": "...",
    "user_input": "...",
    "intake": {...},
    "triage_level": "low|medium|high",
    "urgency_score": 1-10,
    "critic_score": 0-10,
    "final_response": "...",
    "reasoning": [...],
    "red_flags": [...],
    "agent_outputs_count": int,
    "timestamp": "ISO timestamp",
    "latency_ms": float
}
```

### 3. Integration with Pipeline

#### Event Capture

The pipeline now captures all agent outputs during execution:

```python
agent_outputs: List[Dict[str, Any]] = []

for event in runner.run(...):
    # Capture agent outputs
    if event_author and event.content:
        agent_output = {
            "agent": event_author,
            "output": event_text,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "agent_output"
        }
        agent_outputs.append(agent_output)
        
        # Log each agent's decision
        _log_agent_decision(...)
```

#### Session Retrieval

Session history is retrieved and included in context:

```python
recent_history = session_data.get("history", [])[-5:]
history_text = "\nRecent conversation history:\n" + "\n".join(snippets)
composed_message = f"{history_text}\nCurrent user input: {user_message}"
```

### 4. Storage Backends

#### Firestore (Production)

When `firestore_client` is available:
- Stores sessions in `sessions/{session_id}`
- Uses `FirestoreArrayUnion` for history and agent_outputs
- Tracks `total_turns` counter
- Server timestamps for `updated_at`

#### Local Storage (Development/Testing)

When Firestore is not available:
- Uses `LOCAL_SESSION_STORE` dictionary
- Same structure as Firestore
- In-memory storage (cleared on restart)

### 5. Mock Mode Support

Mock mode now also stores sessions:
- Creates mock agent outputs
- Stores to session memory
- Maintains same structure as live mode

## Test Results

### Integration Tests

**8/8 tests passing (100% success rate):**

1. ✅ **test_single_turn_pipeline**: Single turn execution and storage
2. ✅ **test_multi_turn_conversation**: Multi-turn conversation with memory
3. ✅ **test_agent_outputs_stored**: Agent outputs stored in session
4. ✅ **test_session_retrieval**: Session history retrievable
5. ✅ **test_pipeline_agents_execution**: All agents execute correctly
6. ✅ **test_critic_loop_integration**: Critic loop integrated
7. ✅ **test_logging_structure**: Logging structure correct
8. ✅ **test_error_handling_with_logging**: Error handling with logging

### Test Coverage

- ✅ Session storage and retrieval
- ✅ Multi-turn conversations
- ✅ Agent output capture
- ✅ Logging structure
- ✅ Error handling
- ✅ Mock mode compatibility

## Usage

### Accessing Session Data

```python
from agents.multi_agent_pipeline import LOCAL_SESSION_STORE

# Get session data
session_data = LOCAL_SESSION_STORE.get("session_id")
history = session_data["history"]
agent_outputs = session_data["agent_outputs"]
total_turns = session_data["total_turns"]
```

### Querying Logs

**Cloud Logging (Production):**
```python
# Query agent decisions
log_type = "agent_decision"
agent = "IntakeAgent"

# Query final responses
log_type = "final_response"
session_id = "..."
```

### Retrieving Session History

```python
# Session history is automatically retrieved in run_virtual_health_assistant
# Last 5 turns are included in context
response = run_virtual_health_assistant(
    "Follow-up question",
    session_id="existing-session-id"
)
```

## Log Analysis

### Structured Log Format

All logs use structured JSON format for easy analysis:

**Agent Decision Logs:**
- Filter by `log_type: "agent_decision"`
- Filter by `agent: "AgentName"`
- Analyze `parsed_output` for structured data

**Final Response Logs:**
- Filter by `log_type: "final_response"`
- Filter by `triage_level`, `urgency_score`, `critic_score`
- Analyze `agent_outputs_count` for pipeline depth

### Analysis Queries

**Common Queries:**
1. Agent performance: Count decisions by agent
2. Triage distribution: Count by triage_level
3. Quality metrics: Average critic_score
4. Latency analysis: Average latency_ms
5. Session analysis: Total turns per session

## Benefits

### 1. Audit Trail
- Complete record of all agent decisions
- Timestamped logs for compliance
- Structured format for analysis

### 2. Debugging
- Track agent outputs at each step
- Identify where issues occur
- Analyze decision-making process

### 3. Performance Analysis
- Measure latency per agent
- Track critic loop iterations
- Analyze response quality

### 4. Multi-Turn Context
- Maintain conversation history
- Provide context to agents
- Improve response quality

### 5. Compliance
- Structured logging for audit
- Session tracking for accountability
- Complete decision trail

## Future Enhancements

1. **Log Aggregation**: Aggregate logs for analytics
2. **Session Analytics**: Analyze session patterns
3. **Performance Monitoring**: Real-time performance dashboards
4. **Anomaly Detection**: Detect unusual patterns
5. **Export Functionality**: Export logs for external analysis

---

**Last Updated**: 2025-01-15
**Status**: ✅ Implemented and Tested

