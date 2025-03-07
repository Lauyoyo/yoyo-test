import os
import hmac
import hashlib
import json
import requests
import jwt
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv


# Load the .env 
load_dotenv()

# Flask server
app = Flask(__name__)

# GitHub authentication information
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
APP_ID = os.getenv("APP_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")

# Read the GitHub App private key
with open(PRIVATE_KEY_PATH, "r") as key_file:
    PRIVATE_KEY = key_file.read()
    
# Generate JWT for GitHub API
def generate_jwt():
    payload = {
        "iat": int(time.time()),  # Issued at
        "exp": int(time.time()) + 600,  # Expire in 10 minutes
        "iss": APP_ID  # GitHub App ID
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# Get Installation Token
def get_installation_token(installation_id):
    jwt_token = generate_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)
    response_data = response.json()

    if "token" in response_data:
        return response_data["token"]
    else:
        print(f"❌ Failed to obtain the Installation Token: {response_data}")
        return None

# Verify GitHub Webhook Signature
def verify_signature(payload, signature):
    if not signature:
        return False

    mac = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={mac}"
    
    return hmac.compare_digest(expected_signature, signature)

# Listen to the GitHub Webhook
@app.route("/api/webhook", methods=["POST"])
def github_webhook():
    payload = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256")

    # Verify request source
    if not verify_signature(payload, signature):
        return "Invalid signature", 403

    event = request.headers.get("X-GitHub-Event")
    data = json.loads(payload)

    if event == "pull_request":
        pr_number = data["pull_request"]["number"]
        repo_name = data["repository"]["full_name"]
        installation_id = data["installation"]["id"]

        print(f"📢 Received a PR event: #{pr_number} in {repo_name}")
        
         # Get Installation Token
        token = get_installation_token(installation_id)
        if not token:
            return jsonify({"error": "Installation token fetch failed"}), 500
        
        # Send automated comment
        comment_url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        comment_data = {"body": "👋 Hello! Your PR has been detected!"}
        response = requests.post(comment_url, headers=headers, json=comment_data)
        
        if response.status_code == 201:
            print("✅ PR comment success!")
        else:
            print(f"❌ PR comment failed: {response.status_code}, {response.text}")


    elif event == "issues":
        issue_number = data["issue"]["number"]
        repo_name = data["repository"]["full_name"]
        installation_id = data["installation"]["id"]

        print(f"📢 Received Issue event: #{issue_number} in {repo_name}")

        token = get_installation_token(installation_id)
        if not token:
            return jsonify({"error": "Installation token fetch failed"}), 500
        
        comment_url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/comments"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        comment_data = {"body": "📝 Thanks for creating an issue! We'll look into it!"}
        response = requests.post(comment_url, headers=headers, json=comment_data)

        if response.status_code == 201:
            print("✅ Issue comment success！")
        else:
            print(f"❌ Issue comment failed: {response.status_code}, {response.text}")

    elif event == "push":
        repo_name = data["repository"]["full_name"]
        installation_id = data["installation"]["id"]
        pusher = data["pusher"]["name"]
        commits = data["commits"]

        print(f"📢 Received Push event in {repo_name} by {pusher}")

        token = get_installation_token(installation_id)
        if not token:
            return jsonify({"error": "Installation token fetch failed"}), 500

        # Get the latest submission information
        latest_commit = commits[-1]["message"] if commits else "No commit message"

        # Create a new Issue record Push event
        issue_url = f"https://api.github.com/repos/{repo_name}/issues"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        issue_data = {
            "title": f"🚀 New push detected by {pusher}",
            "body": f"New code push detected in **{repo_name}**\n\n"
                    f"🔹 **Pusher**: {pusher}\n"
                    f"🔹 **Latest commit message**: {latest_commit}"
        }
        response = requests.post(issue_url, headers=headers, json=issue_data)

        if response.status_code == 201:
            print("✅ Push event issue created successfully!")
        else:
            print(f"❌ Failed to create push issue: {response.status_code}, {response.text}")


    return jsonify({"status": "success"}), 200

# Start Flask Server
if __name__ == "__main__":
    app.run(port=3000)
