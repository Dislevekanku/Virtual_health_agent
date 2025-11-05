#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhance triage logic with better conditions, explanations, and granular levels
"""

import json
import os
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.oauth2 import service_account
from google.api_core import client_options

# Configuration
SERVICE_ACCOUNT_KEY = "key.json"
AGENT_INFO_FILE = "agent_info.json"
LOCATION = "us-central1"

def load_agent_info():
    """Load agent information"""
    with open(AGENT_INFO_FILE, 'r') as f:
        return json.load(f)

def get_client(client_class):
    """Get a Dialogflow CX client with proper endpoint"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY
    )
    client_options_obj = client_options.ClientOptions(
        api_endpoint=f"{LOCATION}-dialogflow.googleapis.com:443"
    )
    return client_class(credentials=credentials, client_options=client_options_obj)

def enhance_triage_logic():
    """Enhance triage evaluation with better logic and explanations"""
    
    print("="*60)
    print("Enhance Triage Logic")
    print("="*60)
    print()
    
    agent_info = load_agent_info()
    agent_name = agent_info['agent_name']
    
    try:
        # Get flow
        flows_client = get_client(dialogflow.FlowsClient)
        request = dialogflow.ListFlowsRequest(parent=agent_name)
        flows = list(flows_client.list_flows(request=request))
        
        flow_name = None
        for flow in flows:
            if flow.display_name == "Default Start Flow":
                flow_name = flow.name
                break
        
        pages_client = get_client(dialogflow.PagesClient)
        request = dialogflow.ListPagesRequest(parent=flow_name)
        pages = list(pages_client.list_pages(request=request))
        
        triage_page = None
        summary_page = None
        for page in pages:
            if page.display_name == "Triage Evaluation":
                triage_page = page
            if page.display_name == "Summary":
                summary_page = page
        
        if not triage_page:
            print("[ERROR] Triage Evaluation page not found")
            return False
        
        print("Enhancing triage logic...")
        print()
        
        # Clear existing routes
        triage_page.transition_routes = []
        
        # Enhanced conditions with better explanations
        
        # Route 1: Emergency (highest priority)
        emergency_condition = (
            '$session.params.urgency = "high" OR '
            '$session.params.severity_level = "severe" OR '
            '(isDefined($session.params.severity) AND $session.params.severity >= 9) OR '
            '(isDefined($session.params.associated_symptoms) AND $session.params.associated_symptoms.contains("vision") AND $session.params.associated_symptoms.contains("change"))'
        )
        
        emergency_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Based on your symptoms—{symptom_type} with severity {severity}/10—this requires immediate medical attention. "
                            "Given the severity of your symptoms and the information you've provided, I'm concerned about your condition.\n\n"
                            "🚨 **Immediate Action Required:**\n"
                            "• Call your healthcare provider's emergency line immediately, OR\n"
                            "• Go to the nearest emergency department or urgent care center\n\n"
                            "If you're experiencing a life-threatening emergency (chest pain, severe breathing difficulty, loss of consciousness), "
                            "please call 911 immediately.\n\n"
                            "Your safety is our top priority. Please seek medical attention right away."
                        ]
                    )
                )
            ],
            set_parameter_actions=[
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage",
                    value="emergency"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="recommendation",
                    value="Seek immediate medical attention - call emergency line or go to ED"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage_explanation",
                    value="Emergency classification due to high severity (≥9/10) or presence of red flag symptoms requiring immediate evaluation"
                )
            ]
        )
        
        triage_page.transition_routes.append(
            dialogflow.TransitionRoute(
                condition=emergency_condition,
                trigger_fulfillment=emergency_fulfillment,
                target_page=summary_page.name
            )
        )
        print("  [OK] Added emergency route (severity ≥9 or red flags)")
        
        # Route 2: Urgent (same-day care needed)
        urgent_condition = (
            '(isDefined($session.params.severity) AND $session.params.severity >= 7 AND $session.params.severity < 9) OR '
            '(isDefined($session.params.severity) AND $session.params.severity >= 5 AND isDefined($session.params.duration) AND $session.params.duration.contains("week")) OR '
            '(isDefined($session.params.associated_symptoms) AND ($session.params.associated_symptoms.contains("vomit") OR $session.params.associated_symptoms.contains("fever")))'
        )
        
        urgent_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Based on your symptoms—{symptom_type} with severity {severity}/10—this warrants prompt medical evaluation. "
                            "Your symptoms are significant enough that I recommend seeking care today or within 24 hours.\n\n"
                            "⚡ **Recommended Action:**\n"
                            "• Contact your healthcare provider today for same-day appointment, OR\n"
                            "• Visit an urgent care center if you can't reach your provider\n"
                            "• Use our telehealth service if available\n\n"
                            "While this doesn't appear to be immediately life-threatening, your symptoms should be evaluated by a healthcare professional soon."
                        ]
                    )
                )
            ],
            set_parameter_actions=[
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage",
                    value="urgent"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="recommendation",
                    value="Seek same-day care - contact provider today or visit urgent care"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage_explanation",
                    value="Urgent classification due to moderate-high severity (7-8/10) or persistent symptoms requiring prompt evaluation"
                )
            ]
        )
        
        triage_page.transition_routes.append(
            dialogflow.TransitionRoute(
                condition=urgent_condition,
                trigger_fulfillment=urgent_fulfillment,
                target_page=summary_page.name
            )
        )
        print("  [OK] Added urgent route (severity 7-8 or persistent symptoms)")
        
        # Route 3: Same-week (moderate urgency)
        sameweek_condition = (
            '(isDefined($session.params.severity) AND $session.params.severity >= 5 AND $session.params.severity < 7) OR '
            '(isDefined($session.params.duration) AND $session.params.duration.contains("day") AND $session.params.duration != "today" AND $session.params.duration != "yesterday")'
        )
        
        sameweek_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Based on your symptoms—{symptom_type} with severity {severity}/10—I recommend scheduling an appointment with your healthcare provider "
                            "within the next week. While your symptoms don't appear to require immediate attention, they should be evaluated by a medical professional.\n\n"
                            "📅 **Recommended Action:**\n"
                            "• Schedule an appointment with your primary care provider this week\n"
                            "• Use our telehealth service if a same-week appointment isn't available\n"
                            "• Monitor your symptoms and seek care sooner if they worsen\n\n"
                            "Your provider can help determine the cause and appropriate treatment for your symptoms."
                        ]
                    )
                )
            ],
            set_parameter_actions=[
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage",
                    value="same_week"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="recommendation",
                    value="Schedule appointment this week with primary care provider"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage_explanation",
                    value="Same-week classification for moderate symptoms (5-6/10) or symptoms persisting multiple days requiring medical evaluation"
                )
            ]
        )
        
        triage_page.transition_routes.append(
            dialogflow.TransitionRoute(
                condition=sameweek_condition,
                trigger_fulfillment=sameweek_fulfillment,
                target_page=summary_page.name
            )
        )
        print("  [OK] Added same-week route (severity 5-6 or persistent)")
        
        # Route 4: Routine (low urgency - default)
        routine_fulfillment = dialogflow.Fulfillment(
            messages=[
                dialogflow.ResponseMessage(
                    text=dialogflow.ResponseMessage.Text(
                        text=[
                            "Based on your symptoms—{symptom_type} with severity {severity}/10—this may improve with rest and self-care measures. "
                            "Your symptoms appear to be mild and manageable with home care.\n\n"
                            "🏠 **Recommended Action:**\n"
                            "• Rest and monitor your symptoms\n"
                            "• Try basic self-care measures (hydration, rest, over-the-counter pain relief if appropriate)\n"
                            "• Schedule a routine appointment if symptoms persist beyond 3 days or worsen\n\n"
                            "If your symptoms change or you have any concerns, don't hesitate to contact your healthcare provider. "
                            "We're here to help if you need us."
                        ]
                    )
                )
            ],
            set_parameter_actions=[
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage",
                    value="routine"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="recommendation",
                    value="Rest and self-care, monitor symptoms, follow up if persists"
                ),
                dialogflow.Fulfillment.SetParameterAction(
                    parameter="triage_explanation",
                    value="Routine classification for mild symptoms (<5/10) with short duration, typically manageable with self-care"
                )
            ]
        )
        
        triage_page.transition_routes.append(
            dialogflow.TransitionRoute(
                condition="true",  # Default route
                trigger_fulfillment=routine_fulfillment,
                target_page=summary_page.name
            )
        )
        print("  [OK] Added routine route (default - mild symptoms)")
        
        # Update the page
        request = dialogflow.UpdatePageRequest(page=triage_page)
        pages_client.update_page(request=request)
        
        print()
        print("[OK] Triage logic enhanced")
        print()
        print("Improvements:")
        print("  ✓ 4-level triage system: Emergency → Urgent → Same-Week → Routine")
        print("  ✓ Better condition logic with multiple factors")
        print("  ✓ Detailed explanations for each triage level")
        print("  ✓ Clear next steps for each level")
        print("  ✓ Triage explanation stored in parameter")
        print()
        print("Triage Levels:")
        print("  - Emergency: Severity ≥9, red flags, or high urgency")
        print("  - Urgent: Severity 7-8, persistent symptoms, or associated symptoms")
        print("  - Same-Week: Severity 5-6, or symptoms persisting multiple days")
        print("  - Routine: All other cases (mild symptoms, short duration)")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = enhance_triage_logic()
    exit(0 if success else 1)

