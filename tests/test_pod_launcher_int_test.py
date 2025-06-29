from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_run_pod_endpoint(mocker):
    pod_spec = {
        "image": "nginx:latest",
        "name": "test-pod",
        "namespace": "default"
    }

    mock_create = mocker.patch("main.create_pod", return_value={"status": "success", "pod_name": "test-pod", "namespace": "default"})
    response = client.post("/run-pod", json=pod_spec)

    assert response.status_code == 200
    assert response.json() == {"message": "Pod launched", "pod_name": "test-pod", "namespace": "default"}
    mock_create.assert_called_once()

def test_pod_status_success(mocker):
    mock_status = {
        "pod_name": "test-pod",
        "namespace": "default",
        "status": "Running",
        "host_ip": "1.1.1.1",
        "pod_ip": "2.2.2.2",
        "start_time": "2025-06-28T10:00:00Z",
        "conditions": []
    }

    mock_get = mocker.patch("main.get_pod_status", return_value=mock_status)

    response = client.get("/pod-status", params={"name": "test-pod", "namespace": "default"})

    assert response.status_code == 200
    assert response.json()["status"] == "Running"
    mock_get.assert_called_once_with("test-pod", "default")

def test_pod_status_not_found(mocker):
    mock_get = mocker.patch("main.get_pod_status", return_value={"error": "Not found", "details": "No such pod"})

    response = client.get("/pod-status", params={"name": "bad-pod", "namespace": "default"})

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "Not found"
