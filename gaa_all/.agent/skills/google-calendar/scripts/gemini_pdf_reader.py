#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("Error: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key

def upload_file(file_path, mime_type):
    api_key = get_api_key()
    file_size = os.path.getsize(file_path)
    display_name = os.path.basename(file_path)

    # 1. Start Resumable Upload
    url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}"
    
    metadata = {"file": {"display_name": display_name}}
    body = json.dumps(metadata).encode("utf-8")
    
    headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(file_size),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as resp:
            upload_url = resp.headers.get("X-Goog-Upload-URL")
    except urllib.error.HTTPError as e:
        print(f"Error starting upload: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    # 2. Upload Bytes
    with open(file_path, "rb") as f:
        file_data = f.read()
        
    headers = {
        "Content-Length": str(file_size),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize"
    }
    
    req = urllib.request.Request(upload_url, data=file_data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            return result["file"]["uri"]
    except urllib.error.HTTPError as e:
        print(f"Error uploading bytes: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

def generate_content(file_uri, prompt):
    api_key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"file_data": {"mime_type": "application/pdf", "file_uri": file_uri}}
            ]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            if "candidates" in result:
                print(result["candidates"][0]["content"]["parts"][0]["text"])
            else:
                print("No content generated.")
    except urllib.error.HTTPError as e:
        print(f"Error generating content: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: gemini_pdf_reader.py <file_path> <prompt>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    prompt = sys.argv[2]
    
    print("Uploading file to Gemini...", file=sys.stderr)
    uri = upload_file(file_path, "application/pdf")
    print(f"File uploaded: {uri}", file=sys.stderr)
    
    print("Generating summary...", file=sys.stderr)
    generate_content(uri, prompt)
