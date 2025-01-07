import os

import httpx


def get_port():
    # Get models port from ENV parameter.
    port = os.environ.get("MODEL_HANDLER_PORT", "5000")
    return port


def get_models_folder():
    # Get models folder from ENV parameter.
    dir_path = os.environ.get("UPLOAD_DIR", "/workspace/models/inno")

    # check folder path exist
    if not os.path.exists(dir_path):
        raise FileExistsError("Models folder not found.")

    return dir_path


def get_model_server_url(ip: str = "127.0.0.1", port: int = 11434):
    # Get ip folder from ENV parameter.
    ip = os.environ.get("MODEL_SERVER_IP", ip)

    # Get port folder from ENV parameter.
    port = os.environ.get("MODEL_SERVER_PORT", str(port))

    try:
        full_url = check_connection(ip=ip, port=port)
    except Exception as e:
        raise ConnectionError(f"Connect to Model server failed : \n detail \n: {e}")
    return full_url


def check_connection(ip: str, port: int):
    full_url = f"http://{ip}:{port}/"
    try:
        response = httpx.get(full_url, timeout=5)
        if response.status_code == 200:
            print(f"Connection to {full_url} successful!")
            return full_url
        else:
            raise Exception(
                f"Error: Received status code {response.status_code} from {full_url}"
            )

    except httpx.RequestError as e:
        raise Exception(f"Connection failed to {full_url}: {str(e)}")
