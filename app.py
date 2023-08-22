import fastapi
import docker
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()
GITHUB_SECRET = os.environ.get("WEBHOOK_SECRET")

app = fastapi.FastAPI()
client = docker.from_env()


"""
NOTE: Only restarting containers via POST is implemented here. (+ GET for a list of containers)
"""


@app.post("/restart/{container_name}")
async def restart_container(container_name: str):
    if fastapi.Request.headers.get("X-Hub-Signature") == GITHUB_SECRET \
       or not GITHUB_SECRET:
        container = client.containers.get(container_name)
        container.restart()
        return {"message": "Container restarted"}
    return {"message": "Nope"}


@app.get("/containers")
async def get_containers():
    containers = client.containers.list()
    return {"containers": [container.name for container in containers]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
