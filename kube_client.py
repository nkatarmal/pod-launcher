import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from schemas import PodSpec


def load_kube_config():
    """
    Loads Kubernetes configuration for API client authentication.
    First attempts to load in-cluster config for when running inside a pod,
    falls back to local kubeconfig file if not in a cluster environment.
    For the local config, it will use the current context.
    """
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()  # fallback for local testing


def create_pod(spec: PodSpec) -> dict:
    load_kube_config()

    try:
        create_namespace(spec.namespace)
    except ApiException as e:
        return {"status": "error", "details": e.body}

    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=spec.name),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name=spec.name,
                    image=spec.image,
                    command=spec.command,
                    env=[client.V1EnvVar(name=k, value=v) for k, v in (spec.env or {}).items()],
                    resources=client.V1ResourceRequirements(**spec.resources) if spec.resources else None
                )
            ],
            restart_policy="Never"
        )
    )

    try:
        api = client.CoreV1Api()
        created = api.create_namespaced_pod(namespace=spec.namespace, body=pod)
        return {"status": "success", "pod_name": created.metadata.name, "namespace": spec.namespace}
    except ApiException as e:
        try:
            return {"status": "error", "details": json.loads(e.body)}
        except:
            return {"status": "error", "details": e.body}

def get_pod_status(name: str, namespace: str = "default") -> dict:
    load_kube_config()

    v1 = client.CoreV1Api()
    try:
        pod = v1.read_namespaced_pod(name=name, namespace=namespace)
        return {
            "pod_name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "host_ip": pod.status.host_ip,
            "pod_ip": pod.status.pod_ip,
            "start_time": str(pod.status.start_time),
            "conditions": [
                {
                    "type": c.type,
                    "status": c.status,
                    "reason": c.reason,
                    "message": c.message,
                }
                for c in (pod.status.conditions or [])
            ],
        }
    except ApiException as e:
        try:
            return {"error": f"Unable to fetch pod status: {e.reason}", "details": json.loads(e.body)}
        except:
            return {"error": f"Unable to fetch pod status: {e.reason}", "details": e.body}
    
def create_namespace(name: str) -> dict:
    load_kube_config()

    v1 = client.CoreV1Api()
    # check if namespace exists
    try:
        v1.read_namespace(name)
    except ApiException as e:
        # 404 means namespace doesn't exist, so we create it
        if e.status == 404:
            namespace = client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
            return v1.create_namespace(namespace)
        else:
            raise e
