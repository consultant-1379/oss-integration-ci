"""Dynamic cluster management service."""
import os
from os import listdir
from os.path import isfile, join
import re
import subprocess
import json
import requests
from filelock import FileLock
import oyaml as yaml
import uvicorn
from fastapi import FastAPI, HTTPException

KIND_VERSION = os.getenv("KIND_VERSION", "0.17.0")
IMAGE_REGISTRY = "armdockerhub.rnd.ericsson.se"
DEFAULT_NODE_IMAGE = os.getenv("DEFAULT_NODE_IMAGE",
                               IMAGE_REGISTRY + "/kindest/node:v1.25.2")
CLUSTER_IP = os.getenv("CLUSTER_IP", "0.0.0.0")
FREEPORT_IP = os.getenv("FREEPORT_IP", CLUSTER_IP)
FREEPORT_PORT = os.getenv("FREEPORT_PORT", "8081")
FREEPORT_SERVICE = f"http://{FREEPORT_IP}:{FREEPORT_PORT}/freeport"
NODE_SPEC_FILE = "/node_specs/node_api.yaml"

app = FastAPI(
    title="Cluster-mgr",
    description="Cluster-mgr API provides a RESTful wrapper for managing dynamic (KinD-based) clusters",
    version="0.0.1",
)


def get_cluster_config_or_error(cluster_id):
    """
    Return cluster config data, if available.

    Input:
        cluster_id: ID for dynamic cluster

    Output:
        Data structure representing cluster config file
    """
    cluster_config_file = f"/configs/config_{cluster_id}"
    if os.path.exists(cluster_config_file):
        with open(cluster_config_file, "r", encoding="utf-8") as yaml_file:
            cluster_yaml = yaml.safe_load(yaml_file)
            return cluster_yaml
    raise HTTPException(status_code=404, detail="Config not found")


def get_free_port():
    """Return a free port using FREEPORT service."""
    print(f"Contacting {FREEPORT_SERVICE} to resolve a port...")
    # Timeout request after 30s
    port_response = requests.get(FREEPORT_SERVICE, timeout=30)
    if port_response:
        port_response_json = port_response.json()
        print(f"Response: {port_response_json}")
        if "port" in port_response_json:
            return port_response_json["port"]
    raise HTTPException(status_code=404, detail="Could not resolve free port")


@app.get("/ping")
async def ping():
    """General healthcheck endpoint."""
    return {"message": "pong"}


@app.get("/freeport")
async def get_freeport():
    """Endpoint for resolving a free port."""
    return {"port": get_free_port()}


@app.get("/config/{cluster_id}")
async def read_cluster_config(cluster_id):
    """Endpoint to resolve a cluster config."""
    if not cluster_id:
        raise HTTPException(status_code=500, detail="Missing cluster ID")
    return get_cluster_config_or_error(cluster_id)


@app.get("/clusters")
async def get_clusters():
    """Endpoint to return a list of available dynamic clusters."""
    config_files = [c_file for c_file in listdir("/configs") if isfile(join("/configs", c_file))]
    clusters = []
    for config_file in config_files:
        results = re.search("^config_(.+)$", config_file)
        if results:
            clusters.append(results.group(1))
    return {"clusters": clusters}


@app.post("/cluster/{cluster_id}")
# pylint: disable=too-many-locals,too-many-branches
def sync_create_cluster(cluster_id, version: str = "latest",  # noqa: C901
                        control: int = 1, worker: int = 0):
    """Endpoint to generate a new cluster or return existing cluster config (blocking call).

    Input:
        cluster_id: Path parameter for cluster ID to resolve or generate
        version: K8s-compatibility version for nodes (eg. 1.25).
                 Defaults to latest version
        control: Control-plane node count to provision.
                 Default is 1
        worker: Worker node count to provision.
                Default is 0

    Output:
        Cluster configuration data
    """
    if not cluster_id:
        raise HTTPException(status_code=500, detail="Missing cluster ID")
    print(f"Creating cluster {cluster_id}")
    cluster_config_file = f"/configs/config_{cluster_id}"
    if os.path.exists(cluster_config_file):
        # Return the existing cluster config
        return get_cluster_config_or_error(cluster_id)
    if not os.path.exists("/configs"):
        os.makedirs("/configs")
    if not os.path.exists(NODE_SPEC_FILE):
        raise HTTPException(status_code=500, detail="Missing node-API specs")
    node_image = DEFAULT_NODE_IMAGE
    with open(NODE_SPEC_FILE, 'r', encoding="utf-8") as spec_yaml_file:
        spec_yaml = yaml.load(spec_yaml_file, Loader=yaml.CSafeLoader)
        if KIND_VERSION not in spec_yaml:
            raise HTTPException(status_code=500,
                                detail=f"Kind version {KIND_VERSION} not supported")
        if version == "latest":
            api_versions = list(spec_yaml[KIND_VERSION].keys())
            if len(api_versions) == 0:
                raise HTTPException(status_code=500,
                                    detail="Invalid node-API spec (missing API versions)")
            api_versions.sort(reverse=True)
            version = api_versions[0]
        else:
            try:
                version = float(version)
            except Exception as exception:
                raise HTTPException(status_code=500,
                                    detail=f"Invalid node-API version {version}") from exception
            if version not in list(spec_yaml[KIND_VERSION].keys()):
                raise HTTPException(status_code=404,
                                    detail=f"Requested node-API version {version} not in spec")
        node_image = IMAGE_REGISTRY + "/" + spec_yaml[KIND_VERSION][version]
    node_list = []
    for _ in range(control):
        node_list.append({"role": "control-plane"})
    for _ in range(worker):
        node_list.append({"role": "worker"})
    # Note: reason we can't use a dynamic port is because this service (FastAPI) isn't
    # compatible with network-host mode for remote host invocation, not sure why.  As it is,
    # a separate cluster-local service with network-host (freeport) will be used to source
    # a free host port for the cluster
    # "apiServerPort": 0
    lock = FileLock("./port.lock")
    with lock:
        free_port = get_free_port()
        print(f"Configuring cluster with apiServerAddress {CLUSTER_IP} and apiServerPort {free_port}")
        cluster_data = {
            "kind": "Cluster",
            "apiVersion": "kind.x-k8s.io/v1alpha4",
            "networking": {
                "apiServerAddress": CLUSTER_IP,
                "apiServerPort": free_port
            },
            "nodes": node_list
        }
        with open(f"./cluster_setup_{cluster_id}", 'w', encoding="utf-8") as config_yaml_file:
            yaml.safe_dump(cluster_data, config_yaml_file, default_flow_style=False)
        try:
            kind_process = subprocess.run(["/usr/bin/kind", "create",
                                           "cluster", "--kubeconfig",
                                           f"/configs/config_{cluster_id}",
                                           "--image", node_image,
                                           "--name", cluster_id,
                                           "--wait", "5m",
                                           "--config", f"./cluster_setup_{cluster_id}"],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          check=True)
        except Exception as exception:
            print(exception)
            raise HTTPException(status_code=500, detail="Unable to create cluster") from exception
        finally:
            os.remove(f"./cluster_setup_{cluster_id}")
    if kind_process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Unable to create cluster: {kind_process.stderr.decode('utf-8')}")
    return get_cluster_config_or_error(cluster_id)


@app.delete("/cluster/{cluster_id}")
def sync_delete_cluster(cluster_id):
    """Endpoint to delete a cluster by ID.

    Input:
        cluster_id: Path parameter for cluster ID to delete
    """
    if not cluster_id:
        raise HTTPException(status_code=500, detail="Missing cluster ID")
    print(f"Deleting cluster {cluster_id}")
    cluster_config_file = f"/configs/config_{cluster_id}"
    if not os.path.exists(cluster_config_file):
        raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} does not exist")
    try:
        kind_process = subprocess.run(["/usr/bin/kind", "delete",
                                       "clusters", cluster_id],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      check=True)
    except Exception as exception:
        raise HTTPException(status_code=500, detail="Unable to delete cluster") from exception
    if kind_process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Unable to delete cluster: {kind_process.stderr.decode('utf-8')}")
    os.remove(f"/configs/config_{cluster_id}")
    return {"message": f"Cluster {cluster_id} deleted"}


@app.get("/cluster/{cluster_id}")
def sync_get_cluster(cluster_id):  # noqa: C901
    """Endpoint to get a cluster's details by ID.

    Input:
        cluster_id: Path parameter for cluster ID to get details
    """
    if not cluster_id:
        raise HTTPException(status_code=500, detail="Missing cluster ID")
    print(f"Getting cluster {cluster_id}")
    details = {}
    cluster_config_file = f"/configs/config_{cluster_id}"
    if not os.path.exists(cluster_config_file):
        raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} does not exist")
    try:
        kubectl_process = subprocess.run(["/usr/bin/kubectl",
                                          f"--kubeconfig={cluster_config_file}",
                                          "get", "nodes", "-o", "json"],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         check=True)
    except Exception as exception:
        raise HTTPException(status_code=500, detail="Unable to get cluster node details") from exception
    if kubectl_process.returncode != 0:
        raise HTTPException(status_code=500,
                            detail=f"Unable to get cluster node details: {kubectl_process.stderr.decode('utf-8')}")
    cluster_details_json = json.loads(kubectl_process.stdout)
    if "items" in cluster_details_json:
        cluster_nodes = []
        for item in cluster_details_json["items"]:
            if "metadata" in item and \
                 "labels" in item["metadata"] and \
                 "kubernetes.io/hostname" in item["metadata"]["labels"]:
                cluster_nodes.append(item["metadata"]["labels"]["kubernetes.io/hostname"])
        details["nodes"] = cluster_nodes
    try:
        kubectl_process = subprocess.run(["/usr/bin/kubectl",
                                          f"--kubeconfig={cluster_config_file}",
                                          "version", "-o", "json"],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         check=True)
    except Exception as exception:
        raise HTTPException(status_code=500, detail="Unable to get cluster version details") from exception
    if kubectl_process.returncode != 0:
        raise HTTPException(status_code=500,
                            detail=f"Unable to get cluster version details: {kubectl_process.stderr.decode('utf-8')}")
    cluster_details_json = json.loads(kubectl_process.stdout)
    if "serverVersion" in cluster_details_json:
        details["version"] = cluster_details_json["serverVersion"]
    return {"details": details}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get('SERVER_PORT', 8080)), log_level="info")
