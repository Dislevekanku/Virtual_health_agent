#!/usr/bin/env python3
"""
Upload Clinical Guidelines to Google Cloud Storage

This script uploads sanitized clinical guideline files to a GCS bucket
for use with Vertex AI Search and Agent Builder.

Prerequisites:
- GCS bucket created (e.g., 'my-poc-bucket' or 'dfci-guidelines-poc')
- Service account with Storage Admin role
- Environment variable GOOGLE_APPLICATION_CREDENTIALS set to key.json path

Usage:
    python upload_to_gcs.py --bucket my-poc-bucket
    python upload_to_gcs.py --bucket my-poc-bucket --verify
"""

import os
import json
import argparse
from pathlib import Path
from google.cloud import storage
from datetime import datetime


def upload_guidelines_to_gcs(bucket_name, guidelines_dir="guidelines", verify=False):
    """
    Upload all guideline files to GCS bucket
    
    Args:
        bucket_name: Name of the GCS bucket
        guidelines_dir: Local directory containing guideline files
        verify: If True, verify uploads by downloading and comparing
    """
    
    # Initialize GCS client
    try:
        storage_client = storage.Client()
        print(f"✓ Connected to GCS using credentials from: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
    except Exception as e:
        print(f"✗ Failed to initialize GCS client: {e}")
        print("  Make sure GOOGLE_APPLICATION_CREDENTIALS is set to your key.json path")
        return False
    
    # Get or create bucket
    try:
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            print(f"✗ Bucket '{bucket_name}' does not exist")
            print(f"  Create it with: gsutil mb gs://{bucket_name}")
            print(f"  Or via console: https://console.cloud.google.com/storage/create-bucket")
            return False
        print(f"✓ Found bucket: gs://{bucket_name}")
    except Exception as e:
        print(f"✗ Error accessing bucket: {e}")
        return False
    
    # Get list of files to upload
    guidelines_path = Path(guidelines_dir)
    if not guidelines_path.exists():
        print(f"✗ Guidelines directory not found: {guidelines_dir}")
        return False
    
    files_to_upload = list(guidelines_path.glob("*.txt")) + list(guidelines_path.glob("*.json"))
    
    if not files_to_upload:
        print(f"✗ No .txt or .json files found in {guidelines_dir}")
        return False
    
    print(f"\n📁 Found {len(files_to_upload)} files to upload:")
    for f in files_to_upload:
        print(f"   - {f.name}")
    
    # Upload files
    print("\n🚀 Uploading to GCS...")
    uploaded = []
    
    for file_path in files_to_upload:
        blob_name = f"guidelines/{file_path.name}"
        blob = bucket.blob(blob_name)
        
        try:
            # Upload file
            blob.upload_from_filename(str(file_path))
            
            # Set metadata
            blob.metadata = {
                'uploaded_at': datetime.utcnow().isoformat(),
                'source': 'POC Clinical Guidelines',
                'content_type': 'text/plain' if file_path.suffix == '.txt' else 'application/json'
            }
            blob.patch()
            
            print(f"   ✓ Uploaded: gs://{bucket_name}/{blob_name}")
            uploaded.append(blob_name)
            
        except Exception as e:
            print(f"   ✗ Failed to upload {file_path.name}: {e}")
    
    print(f"\n✅ Successfully uploaded {len(uploaded)} / {len(files_to_upload)} files")
    
    # Verify uploads
    if verify:
        print("\n🔍 Verifying uploads...")
        all_verified = True
        for blob_name in uploaded:
            blob = bucket.blob(blob_name)
            if blob.exists():
                size = blob.size
                print(f"   ✓ Verified: {blob_name} ({size} bytes)")
            else:
                print(f"   ✗ Not found: {blob_name}")
                all_verified = False
        
        if all_verified:
            print("\n✅ All files verified successfully")
        else:
            print("\n⚠️ Some files failed verification")
    
    # Display bucket structure
    print(f"\n📊 Bucket structure:")
    print(f"   gs://{bucket_name}/")
    for blob_name in uploaded:
        print(f"     └── {blob_name}")
    
    # Load and display metadata
    metadata_file = guidelines_path / "guidelines_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        print(f"\n📋 Metadata Summary:")
        print(f"   Total documents: {metadata['corpus_info']['total_documents']}")
        print(f"   Version: {metadata['corpus_info']['version']}")
        print(f"   PHI Status: {metadata['corpus_info']['phi_status']}")
    
    # Next steps
    print(f"\n🎯 Next Steps:")
    print(f"   1. Set up Vertex AI Search datastore:")
    print(f"      https://console.cloud.google.com/gen-app-builder/engines")
    print(f"   2. Create a new datastore with:")
    print(f"      - Type: Unstructured documents")
    print(f"      - Import from: Cloud Storage")
    print(f"      - Path: gs://{bucket_name}/guidelines/*.txt")
    print(f"   3. Connect datastore to your Dialogflow CX agent")
    print(f"   4. Enable citations in agent responses")
    
    return True


def list_bucket_contents(bucket_name):
    """List all files in the GCS bucket"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        print(f"\n📂 Contents of gs://{bucket_name}:")
        blobs = list(bucket.list_blobs())
        
        if not blobs:
            print("   (empty)")
            return
        
        for blob in blobs:
            size_kb = blob.size / 1024
            updated = blob.updated.strftime("%Y-%m-%d %H:%M") if blob.updated else "N/A"
            print(f"   {blob.name:<50} {size_kb:>8.1f} KB  {updated}")
        
        print(f"\n   Total: {len(blobs)} files")
        
    except Exception as e:
        print(f"✗ Error listing bucket: {e}")


def create_bucket(bucket_name, project_id, location="us-central1"):
    """Create a new GCS bucket"""
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        bucket.location = location
        bucket.storage_class = "STANDARD"
        
        new_bucket = storage_client.create_bucket(bucket)
        print(f"✓ Created bucket: gs://{new_bucket.name}")
        print(f"  Location: {new_bucket.location}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to create bucket: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Upload clinical guidelines to Google Cloud Storage"
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="GCS bucket name (e.g., 'my-poc-bucket')"
    )
    parser.add_argument(
        "--guidelines-dir",
        default="guidelines",
        help="Local directory containing guideline files (default: guidelines)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify uploads after completion"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List bucket contents instead of uploading"
    )
    parser.add_argument(
        "--create-bucket",
        action="store_true",
        help="Create bucket before uploading"
    )
    parser.add_argument(
        "--project-id",
        help="GCP Project ID (required if creating bucket)"
    )
    
    args = parser.parse_args()
    
    # Check for credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account key file:")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=./key.json")
        return
    
    # Create bucket if requested
    if args.create_bucket:
        if not args.project_id:
            print("✗ --project-id required when creating bucket")
            return
        create_bucket(args.bucket, args.project_id)
        return
    
    # List bucket contents
    if args.list:
        list_bucket_contents(args.bucket)
        return
    
    # Upload files
    success = upload_guidelines_to_gcs(
        bucket_name=args.bucket,
        guidelines_dir=args.guidelines_dir,
        verify=args.verify
    )
    
    if not success:
        print("\n⚠️  Upload failed. Please check errors above.")
        exit(1)
    

if __name__ == "__main__":
    main()

