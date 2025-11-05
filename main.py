#!/usr/bin/env python3
"""
Cloud Function entry point for simplified RAG webhook
Cloud Functions 1st gen HTTP trigger expects a function
"""

import functions_framework
from flask import Request
from rag_simplified import app as flask_app

# Cloud Functions expects a function that handles HTTP requests
# We'll use the Flask app's wsgi_app to handle requests
@functions_framework.http
def app(request: Request):
    """HTTP Cloud Function entry point"""
    # Convert Cloud Functions request to Flask-compatible format
    with flask_app.request_context(request.environ):
        return flask_app.full_dispatch_request()
