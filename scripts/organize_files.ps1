# Organize workspace files for GitHub deployment

Write-Host "Organizing workspace files..." -ForegroundColor Cyan

# Move setup/utility scripts to scripts/
$scriptFiles = @(
    "add_conversation_history.py",
    "add_few_shot_examples.py",
    "add_missing_parameters.py",
    "add_system_instructions_programmatically.py",
    "add_webhook_to_flow.py",
    "add_webhook_to_flow_rest.py",
    "check_and_fix_entry_page.py",
    "check_symptom_intake_page.py",
    "comprehensive_test_and_document.py",
    "configure_agent_builder.py",
    "configure_intent_routes.py",
    "configure_medical_model.py",
    "configure_start_page_routes.py",
    "connect_datastore_manual_guide.py",
    "connect_datastore_to_agent.py",
    "connect_generator_datastore.py",
    "create_agent.py",
    "create_datastore_simple.py",
    "create_flows.py",
    "debug_and_fix_routing.py",
    "deploy_grounding_tool.py",
    "deploy_production_rag.py",
    "deploy_webhook.py",
    "diagnose_routes.py",
    "diagnose_webhook_issue.py",
    "enhance_triage_logic.py",
    "find_and_fix_datastore.py",
    "fix_all_message_issues.py",
    "fix_clarifying_questions_page.py",
    "fix_duplicate_messages.py",
    "fix_duration_extraction.py",
    "fix_duration_parameter_issue.py",
    "fix_flow_entry_point.py",
    "fix_flow_routes_to_collect_params.py",
    "fix_parameter_extraction.py",
    "fix_parameter_substitution.py",
    "fix_triage_parameter_logic.py",
    "fix_webhook_database_access.py",
    "fix_webhook_programmatically.py",
    "improve_conversation_flow.py",
    "improve_parameter_extraction.py",
    "improve_webhook_fallback.py",
    "integrate_grounding_webhook.py",
    "personalize_responses.py",
    "polish_conversation_flow.py",
    "programmatic_agent_builder_integration.py",
    "setup_vertex_search.py",
    "test_webhook.py",
    "upload_to_gcs.py",
    "verify_and_enhance_intents.py",
    "verify_and_fix_complete_flow.py",
    "verify_and_fix_entry_point.py",
    "verify_clarifying_questions.py",
    "verify_complete_setup.py"
)

foreach ($file in $scriptFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "scripts\" -Force -ErrorAction SilentlyContinue
        Write-Host "  Moved: $file" -ForegroundColor Gray
    }
}

# Move PowerShell scripts to scripts/
$psFiles = Get-ChildItem -Filter "*.ps1" | Where-Object { $_.Name -ne "organize_files.ps1" }
foreach ($file in $psFiles) {
    Move-Item -Path $file.FullName -Destination "scripts\" -Force -ErrorAction SilentlyContinue
    Write-Host "  Moved: $($file.Name)" -ForegroundColor Gray
}

# Move shell scripts to scripts/
$shFiles = Get-ChildItem -Filter "*.sh"
foreach ($file in $shFiles) {
    Move-Item -Path $file.FullName -Destination "scripts\" -Force -ErrorAction SilentlyContinue
    Write-Host "  Moved: $($file.Name)" -ForegroundColor Gray
}

# Move documentation to docs/
$docFiles = @(
    "ADD_DATASTORE_TO_FLOW.md",
    "ADD_SYSTEM_INSTRUCTIONS_GUIDE.md",
    "AGENT_IMPROVEMENT_RECOMMENDATIONS.md",
    "AGENT_READY.md",
    "AGENT_BUILDER_INTEGRATION.md",
    "agent_builder_grounding_integration.md",
    "COMPLETE_AGENT_BUILDER_SETUP.md",
    "CONNECT_DATASTORE_MANUAL_GUIDE.md",
    "CONNECT_DATASTORE_STEPS.md",
    "CORPUS_SETUP_GUIDE.md",
    "DIALOGFLOW_INTEGRATION.md",
    "DURATION_FIX_SUMMARY.md",
    "FINAL_SETUP_STEPS.md",
    "FIND_AGENT_SETTINGS.md",
    "FIXES_SUMMARY.md",
    "FRONTEND_README.md",
    "FRONTEND_SETUP_COMPLETE.md",
    "GCP_SETUP_VERIFICATION.md",
    "IMPROVEMENTS_IMPLEMENTED.md",
    "KNOWLEDGE_BASE_SUMMARY.md",
    "MANUAL_WEBHOOK_INTEGRATION.md",
    "MEDICAL_MODEL_CONFIGURATION.md",
    "MESSAGE_FIXES_SUMMARY.md",
    "NEXT_STEPS_UI_SETUP.md",
    "POLISHING_SUMMARY.md",
    "PROJECT_SUMMARY.md",
    "QUICK_FIX_AGENT_SETTINGS.md",
    "QUICK_START.md",
    "QUICK_WEBHOOK_FIX.md",
    "RAG_INTEGRATION_GUIDE.md",
    "SUMMARY_OF_WORK.md",
    "TEST_RESULTS.md",
    "TEST_RESULTS_TABLE.md",
    "UI_CREATION_GUIDE.md",
    "UI_NAVIGATION_HELP.md",
    "USE_CASES_AND_DEMO_PLAN.md",
    "VERTEX_SEARCH_MANUAL_SETUP.md",
    "WEBHOOK_TROUBLESHOOTING_SUMMARY.md",
    "fix_webhook_integration.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "docs\" -Force -ErrorAction SilentlyContinue
        Write-Host "  Moved: $file" -ForegroundColor Gray
    }
}

# Move test files to tests/
$testFiles = @(
    "test_agent.py",
    "test_scenarios.json",
    "test_results.json"
)

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "tests\" -Force -ErrorAction SilentlyContinue
        Write-Host "  Moved: $file" -ForegroundColor Gray
    }
}

# Move configuration templates to config/
if (Test-Path "conversation_flow.json") {
    New-Item -ItemType Directory -Force -Path "config" | Out-Null
    Move-Item -Path "conversation_flow.json" -Destination "config\" -Force -ErrorAction SilentlyContinue
    Write-Host "  Moved: conversation_flow.json" -ForegroundColor Gray
}

if (Test-Path "response_templates.json") {
    Move-Item -Path "response_templates.json" -Destination "config\" -Force -ErrorAction SilentlyContinue
    Write-Host "  Moved: response_templates.json" -ForegroundColor Gray
}

if (Test-Path "training_examples.json") {
    Move-Item -Path "training_examples.json" -Destination "config\" -Force -ErrorAction SilentlyContinue
    Write-Host "  Moved: training_examples.json" -ForegroundColor Gray
}

Write-Host "`nOrganization complete!" -ForegroundColor Green
Write-Host "Files organized into:" -ForegroundColor Cyan
Write-Host "  - scripts/  (setup and utility scripts)" -ForegroundColor White
Write-Host "  - docs/    (documentation)" -ForegroundColor White
Write-Host "  - tests/   (test files)" -ForegroundColor White
Write-Host "  - config/  (configuration templates)" -ForegroundColor White

