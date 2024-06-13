import sys
import os
import requests

def upload_zip_file(username, api_token, artifact_file_path):
    # Construct the upload URL based on PythonAnywhere API documentation
    api_base_url = "https://www.eu.pythonanywhere.com/api/v0"
    upload_url = f"{api_base_url}/user/{username}/files/path/home/{username}/{artifact_file_path}"

    # Ensure the zip file exists
    if not os.path.exists(artifact_file_path):
        print(f"Error: Zip file '{artifact_file_path}' not found.")
        return

    # Open the zip file to upload
    with open(artifact_file_path, 'rb') as file:
        headers = {'Authorization': f'Token {api_token}'}
        files = {'content': file}

        try:
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()
            print(f"File uploaded successfully. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error uploading file: {e}")

if __name__ == "__main__":
    # Check if username, api_token, and zip_file_path are provided as arguments
    if len(sys.argv) != 4:
        print("Usage: python upload_artifact.py <username> <api_token> <artifact_file_path>")
        sys.exit(1)

    username = sys.argv[1]
    api_token = sys.argv[2]
    artifact_file_path = sys.argv[3]

    upload_zip_file(username, api_token, artifact_file_path)
