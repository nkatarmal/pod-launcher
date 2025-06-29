from fastapi import FastAPI, HTTPException, Query
from schemas import PodSpec
from kube_client import create_pod, get_pod_status

app = FastAPI(
    title="Kubernetes Pod Launcher",
    description="API to launch and monitor Kubernetes pods",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# endpoint to run a pod
@app.post("/run-pod")
async def run_pod(pod_spec: PodSpec):
    result = create_pod(pod_spec)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["details"])
    return {"message": "Pod launched", "pod_name": result["pod_name"], "namespace": result["namespace"]}

# endpoint to get the status of a pod
@app.get("/pod-status")
async def pod_status(
    name: str = Query(..., description="Name of the pod"),
    namespace: str = Query("default", description="Namespace of the pod")
):
    result = get_pod_status(name, namespace)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result