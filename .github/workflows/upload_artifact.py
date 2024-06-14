import sys
import os
import requests

def main():
    if len(sys.argv) < 4:
        print("Usage: python ./github/workflows/upload_artifact.py PA_USERNAME PA_API_TOKEN ARTIFACT_PATH")
        sys.exit(1)

    pa_username = sys.argv[1]
    pa_api_token = sys.argv[2]
    artifact_path = sys.argv[3]
    try:
        upload_artifact(pa_username, pa_api_token, artifact_path)
    except Exception as e:
        print(e)
        sys.exit(1)

def upload_artifact(username, api_token, artifact_path):
    api_base_url = "https://eu.pythonanywhere.com/api/v0"
    upload_url = f"{api_base_url}/user/{username}/files/path/home/{username}/web_app/{artifact_path}"

    # Ensure the zip file exists
    if not os.path.exists(artifact_path):
        print(f"Error: Artifact '{artifact_path}' not found.")
        return

    # Open the zip file to upload
    with open(artifact_path, 'rb') as file:
        headers = {'Authorization': f'Token {api_token}'}
        files = {'content': file}

        try:
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()
            print(f"Artifact uploaded successfully. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            msg = f"Error uploading Artifact: {e}"
            raise Exception(msg)

if __name__ == "__main__":
    main()
