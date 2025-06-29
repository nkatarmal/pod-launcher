from pydantic import BaseModel, Field
from typing import Optional, Dict


class PodSpec(BaseModel):
    """
    Specification for creating a Kubernetes Pod.

    Attributes:
        image: Docker image to use for the container
        name: Name of the pod
        namespace: Kubernetes namespace to create the pod in (defaults to "default")
        command: Optional list of commands to run in the container
        env: Optional dictionary of environment variables to set in the container
        resources: Optional resource requirements and limits for the container
                  (e.g. {"limits": {"cpu": "500m", "memory": "128Mi"}})
    """
    image: str = Field(..., example="nginx:latest")
    name: str = Field(..., example="custom-nginx") 
    namespace: str = Field(default="default")
    command: Optional[list[str]] = None
    env: Optional[Dict[str, str]] = None
    resources: Dict[str, Dict[str, str]] = Field(
        default={
            "requests": {"cpu": "100m", "memory": "64Mi"},
            "limits": {"cpu": "500m", "memory": "128Mi"}
        },
        example={"limits": {"cpu": "500m", "memory": "128Mi"}}
    )
