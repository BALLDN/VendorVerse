import sys
import os
import requests

API_BASE_URL = "https://eu.pythonanywhere.com/api/v0"

def main():
    if len(sys.argv) < 5:
        print("Usage: python ./github/workflows/deploy_script.py PA_USERNAME PA_API_TOKEN PA_CONSOLE_ID ARTIFACT_PATH")
        sys.exit(1)

    pa_username = sys.argv[1]
    pa_api_token = sys.argv[2]
    pa_console_id = sys.argv[3]
    artifact_path = sys.argv[4]

    try:
        upload_artifact(pa_username, pa_api_token, artifact_path)
        setup_prod_env(pa_username, pa_api_token, pa_console_id, artifact_path)
        reload_web_app(pa_username, pa_api_token)
    except Exception as e:
        print(e)
        sys.exit(1)

def upload_artifact(username, api_token, artifact_path):
    upload_url = f"{API_BASE_URL}/user/{username}/files/path/home/{username}/web_app/{os.path.basename(artifact_path)}"

    if not os.path.exists(artifact_path):
        print(f"Error: Artifact '{artifact_path}' not found.")
        return

    with open(artifact_path, 'rb') as file:
        headers = {'Authorization': f'Token {api_token}'}
        files = {'content': file}

        try:
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()
            print(f"Artifact upload successful. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            msg = f"Error uploading artifact: {e}"
            raise Exception(msg)

def setup_prod_env(username, api_token, console_id, artifact_path):
    console_url = f"{API_BASE_URL}/user/{username}/consoles/{console_id}/send_input"
    headers = {'Authorization': f'Token {api_token}'}
    
    commands = f"""
    cd ~/web_app
    find . -type f ! -name '{artifact_path}' -delete
    unzip {artifact_path}
    source ~/.bashrc
    workon prod_venv
    pip install -r requirements.txt
    """

    data = {'input': commands}

    try:
        response = requests.post(console_url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Environment setup successful. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        msg = f"Error setting up environment: {e}"
        raise Exception(msg)

def reload_web_app(username, api_token):
    reload_url = f"{API_BASE_URL}/user/{username}/webapps/vendorverse.eu.pythonanywhere.com/reload/"
    headers = {'Authorization': f'Token {api_token}'}

    try:
        response = requests.post(reload_url, headers=headers)
        response.raise_for_status()
        print(f"Web app reload successful. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        msg = f"Error reloading web app: {e}"
        raise Exception(msg)

if __name__ == "__main__":
    main()
