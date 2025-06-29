# pod-launcher
Simple python API service which can deploy pods to kubernetes cluster. This uses FastAPI and python kubernetes client to launch the pods in kubernets cluster. Current setup can be tested easily using the local Docker-compose setup.


## How to run

Before you run this application make sure that from your machine you can connect to the Kubernetes cluster where you intend to create the pods and your kubeconfig is setup correctly in the `$HOME/.kube` directory. If you are using EKS cluster than make sure you uncomment the last line in the `docker-compose.yaml` file.

NOTE: By default it will use the current context from your kubeconfig file in a case you have multiple contexts in it.

Run the below command to start the application:
```
docker-compose up --build
```

This will start the fast API server and you can access the swagger docs at http://localhost:8000/docs. From there you can test the application.

This can extended to be deployed in the kubernetes as well as a deployment, where we can create a service account and use the ClusterRoleBinding to attach necessary permissions to the service account and than we can deploy this inside a kubernetes cluster to create pods in the same cluster it is running in.

