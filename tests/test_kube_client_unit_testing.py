import pytest
from unittest.mock import patch, MagicMock
from kube_client import create_pod, get_pod_status
from schemas import PodSpec

@pytest.fixture
def sample_spec():
    return PodSpec(
        image="nginx:latest",
        name="test-pod",
        namespace="default",
        env={"TEST_ENV": "123"},
        resources={"limits": {"cpu": "100m", "memory": "64Mi"}}
    )

@patch("kube_client.config.load_kube_config")
@patch("kube_client.client.CoreV1Api")
def test_create_pod(mock_api_class, mock_kube_config, sample_spec):
    mock_api = MagicMock()
    mock_api.create_namespaced_pod.return_value.metadata.name = sample_spec.name
    mock_api_class.return_value = mock_api

    result = create_pod(sample_spec)
    assert result["status"] == "success"
    assert result["pod_name"] == "test-pod"

@patch("kube_client.config.load_kube_config")
@patch("kube_client.client.CoreV1Api")
def test_get_pod_status(mock_api_class, mock_kube_config):
    mock_pod = MagicMock()
    mock_pod.metadata.name = "demo"
    mock_pod.metadata.namespace = "default"
    mock_pod.status.phase = "Running"
    mock_pod.status.host_ip = "10.0.0.1"
    mock_pod.status.pod_ip = "172.17.0.1"
    mock_pod.status.start_time = "2025-06-28T10:23:45Z"
    mock_pod.status.conditions = []

    mock_api = MagicMock()
    mock_api.read_namespaced_pod.return_value = mock_pod
    mock_api_class.return_value = mock_api

    result = get_pod_status("demo", "default")
    assert result["status"] == "Running"
    assert result["pod_name"] == "demo"

@patch("kube_client.config.load_kube_config")
@patch("kube_client.client.CoreV1Api")
def test_create_namespace(mock_api_class, mock_kube_config):
    mock_api = MagicMock()
    mock_api.create_namespace.return_value.metadata.name = "default"
    mock_api_class.return_value = mock_api