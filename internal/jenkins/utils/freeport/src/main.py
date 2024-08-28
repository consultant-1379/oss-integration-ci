"""Generic port management service."""
import os
import socket
import uvicorn
from fastapi import FastAPI

CLUSTER_IP = os.getenv("CLUSTER_IP", "0.0.0.0")
app = FastAPI()


@app.get("/ping")
async def ping():
    """Healthcheck response endpoint."""
    return {"message": "pong"}


@app.get("/freeport")
async def freeport():
    """Return a free host port."""
    sock = socket.socket()
    sock.bind((CLUSTER_IP, 0))
    port = sock.getsockname()[1]
    return {"port": port}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get('SERVER_PORT', 8080)), log_level="info")
