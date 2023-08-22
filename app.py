import hashlib
import hmac
import json
import os
from typing import Annotated

import docker
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header, HTTPException

load_dotenv()
GITHUB_SECRET = os.environ.get("WEBHOOK_SECRET")

app = FastAPI()
client = docker.from_env()

"""
NOTE: Only restarting containers via POST is implemented here.

See Github Webhook documentation for more information:
https://docs.github.com/en/webhooks-and-events/webhooks/about-webhooks
"""


def verify_signature(payload_body, secret_token, signature_header) -> None:
    """Verify that the payload was sent from GitHub by validating SHA256.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise HTTPException(status_code=403, detail="No signature header received!")
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Invalid signature!")


def container_from_name(name) -> docker.models.containers.Container:
    return [container for container in client.containers.list() if container.name == name][0]


@app.post("/restart/{container_name}")
async def restart_container(container_name: str,
                            request: Request,
                            x_hub_signature_256: Annotated[str, Header()] = None):
    """Restart a container by name."""
    verify_signature(await request.body(), GITHUB_SECRET, x_hub_signature_256)
    container_from_name(container_name).restart()
    return {"message": "Container restarted"}


@app.post("/restart-passing-workflow/{container_name}/{workflow_name}")
async def restart_passing_workflow(container_name: str,
                                   workflow_name: str,
                                   request: Request,
                                   x_hub_signature_256: Annotated[str, Header()] = None):
    """Restart a container by name only if a specific workflow is passing."""
    body = await request.body()
    verify_signature(body, GITHUB_SECRET, x_hub_signature_256)

    payload = json.loads(body)

    if 'workflow_run' not in payload:
        raise HTTPException(status_code=403, detail="No workflow_run in payload!")
    if not payload["workflow_run"]["name"] == workflow_name:
        raise HTTPException(status_code=400, detail="Wrong workflow name!")
    if not payload["workflow_run"]["conclusion"] == "success":
        raise HTTPException(status_code=400, detail="Workflow still running or failed!")

    container_from_name(container_name).restart()
    return {"message": "Container restarted"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
