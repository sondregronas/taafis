import hashlib
import hmac
import os
from typing import Annotated

import docker
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header

load_dotenv()
GITHUB_SECRET = os.environ.get("WEBHOOK_SECRET")

app = FastAPI()
client = docker.from_env()

"""
NOTE: Only restarting containers via POST is implemented here.
"""


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise ValueError("x-hub-signature-256 header is missing!")
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise ValueError("Request signatures didn't match!")


@app.post("/restart/{container_name}")
async def restart_container(container_name: str,
                            request: Request,
                            x_hub_signature_256: Annotated[str, Header()] = None):
    if x_hub_signature_256 is None:
        return {"message": "Missing signature"}

    try:
        verify_signature(await request.body(), GITHUB_SECRET, x_hub_signature_256)
    except ValueError as e:
        return {"message": e}

    target = [container for container in client.containers.list() if container.name == container_name][0]
    target.restart()
    print(f"Container {container_name} restarted")
    return {"message": "Container restarted"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
