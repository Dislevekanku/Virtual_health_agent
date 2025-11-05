#!/usr/bin/env python3
"""
Deploy Clinical Guidelines Webhook to Cloud Functions

This script deploys the search_webhook.py as a Cloud Function
that can be called by Dialogflow CX.
"""

import os
import subprocess
import json

# Configuration
PROJECT_ID = "ai-agent-health-assistant"
FUNCTION_NAME = "clinical-guidelines-webhook"
REGION = "us-central1"
RUNTIME = "python311"
ENTRY_POINT = "webhook"

def deploy_cloud_function():
    """Deploy the webhook as a Cloud Function"""
    
    print("=" * 80)
    print("DEPLOYING CLINICAL GUIDELINES WEBHOOK")
    print("=" * 80)
    
    # Check if gcloud is available
    try:
        result = subprocess.run([
            "C:\\Users\\dk032\\AppData\\Local\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd",
            "version"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("✗ gcloud not found. Please ensure gcloud is installed and in PATH.")
            return False
            
        print("✓ gcloud found")
        
    except Exception as e:
        print(f"✗ Error checking gcloud: {e}")
        return False
    
    # Check credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("\n⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account key file:")
        print("   $env:GOOGLE_APPLICATION_CREDENTIALS=\".\\key.json\"")
        return False
    
    print(f"✓ Using credentials: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    # Create requirements.txt for Cloud Function
    requirements_content = """flask==3.0.0
google-cloud-discoveryengine==0.13.12
google-cloud-functions-framework==3.5.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print(f"\n📦 Created requirements.txt")
    
    # Deploy Cloud Function
    print(f"\n🚀 Deploying Cloud Function...")
    print(f"   Function name: {FUNCTION_NAME}")
    print(f"   Region: {REGION}")
    print(f"   Runtime: {RUNTIME}")
    
    try:
        cmd = [
            "C:\\Users\\dk032\\AppData\\Local\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd",
            "functions", "deploy", FUNCTION_NAME,
            "--runtime", RUNTIME,
            "--trigger-http",
            "--allow-unauthenticated",
            "--source", ".",
            "--entry-point", ENTRY_POINT,
            "--region", REGION,
            "--project", PROJECT_ID,
            "--memory", "512MB",
            "--timeout", "540s"
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ Cloud Function deployed successfully!")
            
            # Extract the function URL from output
            output_lines = result.stdout.split('\n')
            function_url = None
            
            for line in output_lines:
                if 'url:' in line.lower():
                    function_url = line.split('url:')[1].strip()
                    break
            
            if function_url:
                print(f"\n🔗 Function URL: {function_url}")
                print(f"   Webhook endpoint: {function_url}/webhook")
                print(f"   Test endpoint: {function_url}/test")
                print(f"   Health check: {function_url}/health")
                
                # Save URL to file for easy reference
                with open("webhook_url.txt", "w") as f:
                    f.write(f"Webhook URL: {function_url}/webhook\n")
                    f.write(f"Test URL: {function_url}/test\n")
                    f.write(f"Health URL: {function_url}/health\n")
                
                print(f"\n📝 URLs saved to webhook_url.txt")
                
            return True
            
        else:
            print(f"\n✗ Deployment failed:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"\n✗ Deployment error: {e}")
        return False

def test_deployment(function_url):
    """Test the deployed function"""
    
    print(f"\n🧪 Testing deployment...")
    
    try:
        import requests
        
        # Test health endpoint
        health_url = f"{function_url}/health"
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            print(f"   ✓ Health check passed")
        else:
            print(f"   ✗ Health check failed: {response.status_code}")
            return False
        
        # Test search endpoint
        test_url = f"{function_url}/test"
        test_data = {
            "query": "What are red flag headache symptoms?"
        }
        
        response = requests.post(test_url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Search test passed")
            print(f"   Query: {result.get('query', 'N/A')}")
            print(f"   Triage level: {result.get('triage_level', 'N/A')}")
            print(f"   Citations: {len(result.get('citations', []))}")
        else:
            print(f"   ✗ Search test failed: {response.status_code}")
            return False
        
        return True
        
    except ImportError:
        print(f"   ⚠️  requests library not available for testing")
        print(f"   You can test manually at: {function_url}/test")
        return True
    except Exception as e:
        print(f"   ⚠️  Test error: {e}")
        print(f"   Function deployed but testing failed")
        return True

def create_dialogflow_integration_instructions(function_url):
    """Create instructions for integrating with Dialogflow CX"""
    
    instructions = f"""
# Dialogflow CX Integration Instructions

## Webhook URL
{function_url}/webhook

## Integration Steps

### 1. Configure Webhook in Dialogflow CX
1. Go to your Dialogflow CX agent
2. Go to **Manage** → **Webhooks**
3. Click **"+ Create Webhook"**
4. **Webhook name**: `clinical-guidelines-webhook`
5. **Webhook URL**: `{function_url}/webhook`
6. **Authentication**: None (unauthenticated)
7. Click **"Save"**

### 2. Add Webhook to Flow
1. Go to **Build** → **Default Start Flow**
2. Click on **"Start Page"**
3. In **"Fulfillment"** section:
   - Click **"+ Add dialogue option"**
   - Select **"Call webhook"**
   - Select: `clinical-guidelines-webhook`
4. Click **"Save"**

### 3. Test Integration
1. Go to **Preview** panel
2. Type: `What are red flag headache symptoms?`
3. Should return clinical guidelines with citations

## Test Endpoints

- **Webhook**: `{function_url}/webhook`
- **Direct Test**: `{function_url}/test`
- **Health Check**: `{function_url}/health`

## Example Test Request
```bash
curl -X POST {function_url}/test \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "What are red flag headache symptoms?"}}'
```

## Features
- ✅ Clinical guidelines search
- ✅ Red flag detection
- ✅ Triage recommendations (emergency/urgent/routine)
- ✅ Citations with document IDs
- ✅ Dialogflow CX integration
"""
    
    with open("DIALOGFLOW_INTEGRATION.md", "w") as f:
        f.write(instructions)
    
    print(f"\n📋 Integration instructions saved to DIALOGFLOW_INTEGRATION.md")

def main():
    """Main deployment process"""
    
    success = deploy_cloud_function()
    
    if success:
        # Read the webhook URL from the saved file
        try:
            with open("webhook_url.txt", "r") as f:
                url_line = f.readline()
                function_url = url_line.split("Webhook URL: ")[1].strip()
            
            # Test deployment
            test_deployment(function_url)
            
            # Create integration instructions
            create_dialogflow_integration_instructions(function_url)
            
            print(f"\n" + "=" * 80)
            print("✅ DEPLOYMENT COMPLETE")
            print("=" * 80)
            print(f"\n🎯 Next Steps:")
            print(f"   1. Follow instructions in DIALOGFLOW_INTEGRATION.md")
            print(f"   2. Configure webhook in Dialogflow CX")
            print(f"   3. Test with clinical queries")
            print(f"   4. Your agent now has clinical guidelines knowledge!")
            
        except Exception as e:
            print(f"\n⚠️  Deployment successful but couldn't extract URL: {e}")
            print(f"   Check Cloud Functions console for the URL")
    
    else:
        print(f"\n✗ Deployment failed. Check errors above.")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main()
