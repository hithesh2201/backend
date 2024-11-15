from flask import Flask, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route("/get-embed-info", methods=["GET"])
def get_embed_token():
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    workspace_id = "883daf4b-6b56-40a9-83f2-56d8b52a48cc"
    report_id = "f3446f80-6d80-49cb-93be-470f53f83fdf"

    try:
        # Step 1: Authenticate with Azure AD
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")

        # Step 2: Get Embed URL
        embed_url_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}"
        embed_url_headers = {"Authorization": f"Bearer {access_token}"}
        embed_url_response = requests.get(embed_url_endpoint, headers=embed_url_headers)
        embed_url_response.raise_for_status()
        embed_url = embed_url_response.json().get("embedUrl")

        # Step 3: Get Embed Token
        embed_token_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"
        embed_token_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        embed_token_data = {"accessLevel": "view"}
        embed_token_response = requests.post(embed_token_endpoint, headers=embed_token_headers, json=embed_token_data)
        embed_token_response.raise_for_status()
        embed_token = embed_token_response.json().get("token")

        return jsonify({"embedUrl": embed_url, "embedToken": embed_token})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
