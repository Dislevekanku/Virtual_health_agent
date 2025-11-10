# Knowledge Grounding Playbook

This guide documents how the Virtual Health Assistant grounds responses in clinical guidance using Vertex AI Search and Gemini.

## 1. Curate Clinical Guidance Corpus

- Collect public clinical references (CDC, Mayo Clinic, NIH, synthetic summaries) in `guidelines/` as `.txt` files.
- Run the helper script to produce a Discovery Engine–ready JSONL file:

```bash
python scripts/prepare_vertex_search_corpus.py \
  --source-dir guidelines \
  --output artifacts/vertex_search_corpus.jsonl
```

## 2. Update Vertex AI Search Index

1. Create (or reuse) a Search Engine in Vertex AI Search / Discovery Engine.
2. Upload `artifacts/vertex_search_corpus.jsonl` via:
   - **Console**: Data → Import documents → JSONL (Cloud Storage or local upload), or
   - **CLI**:
     ```bash
     gsutil cp artifacts/vertex_search_corpus.jsonl gs://YOUR_BUCKET/
     gcloud discovery-engine data-stores documents import \
       --project=PROJECT_ID \
       --location=global \
       --data-store=clinical-guidelines-datastore \
       --gcs-uri=gs://YOUR_BUCKET/artifacts/vertex_search_corpus.jsonl \
       --auto-generate-ids
     ```
3. Confirm documents are indexed and include metadata (`title`, `source`, `snippet`).

## 3. Webhook Integration

- `rag_simplified.py` calls Discovery Engine, generates Gemini responses, and prepends an explicit grounding section:

  > According to clinical guidance:  
  > \[1] Mayo Clinic – Lightheadedness — Mayo Clinic  
  > …
- The webhook returns both the grounded message and structured citation metadata (`payload.grounding_sources`) so Dialogflow CX or downstream services can render source links.

## 4. Dialogflow CX Usage

- Attach the webhook to intents/pages that require evidence-based reasoning (e.g., triage evaluation).
- Configure responses to surface citations:
  - Include `According to clinical guidance…` text in the fulfillment message.
  - Optionally render citations in the frontend using `payload.grounding_sources`.

## 5. Verification & Testing

- Use the `/test` endpoint (or scripted tests) to validate sample queries:
  ```bash
  curl -X POST http://localhost:8080/test \
    -H "Content-Type: application/json" \
    -d '{"query": "I feel lightheaded but no chest pain"}'
  ```
- Ensure the JSON response includes:
  - `answer` containing the guidance preamble.
  - `grounding_sources` listing titles/sources.
  - `citations` referencing Discovery Engine document IDs.

- Automated unit test `tests/test_grounding_format.py` asserts that grounded responses include the expected prefix and citations.

## 6. Future Enhancements

- Expand corpus with localized or organization-specific protocols.
- Store provenance metadata (URL, publication date) for richer citations.
- Add guardrails to handle conflicting sources or low-confidence search results.

