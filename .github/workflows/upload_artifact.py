import sys
import os
import requests

def upload_zip_file(username, api_token, artifact_path):
    # Construct the upload URL based on PythonAnywhere API documentation
    api_base_url = "https://eu.pythonanywhere.com/api/v0"
    upload_url = f"{api_base_url}/user/{username}/files/path/home/{username}/web_app/{artifact_path}"

    # Ensure the zip file exists
    if not os.path.exists(artifact_path):
        print(f"Error: Zip file '{artifact_path}' not found.")
        return

    # Open the zip file to upload
    with open(artifact_path, 'rb') as file:
        headers = {'Authorization': f'Token {api_token}'}
        files = {'content': file}

        try:
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()
            print(f"File uploaded successfully. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            msg = f"Error uploading file: {e}"
            print(msg)
            raise Exception(msg)

if __name__ == "__main__":

    username = sys.argv[1]
    if username:
        print("No username provided")
        sys.exit(1)
    api_token = sys.argv[2]
    if api_token:
        print("No api_token provided")
        sys.exit(1)
    artifact_path = sys.argv[3]
    if artifact_path:
        print("No artifact_path provided")
        sys.exit(1)
        
    if len(sys.argv) != 4:
        print("Usage: python upload_artifact.py <username> <api_token> <artifact_path>")
        sys.exit(1)
    try:
        upload_zip_file(username, api_token, artifact_path)
    except Exception as e:
        print(e)
        sys.exit(1)
