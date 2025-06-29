Before answering these question i would like to mention that reason i choose fastAPI as it is very simple and quick to start with for a small scale project, without extra configuration that is needed in a heavy framework like Django.


1. Security
Imagine such a system in production, where anyone could deploy a service through it. 
What things should be considered to ensure the system is secure, as we would be effectively executing the third party code.
Such a service could have access to sensitive information such as private keys that are used to manage assets on-chain. How would you go about managing this sensitive information?

- <b>ANSWER: </b> There are 2 aspects of this system, Code security and the secretes security. For Code security when we have request to deploy a new pod we can first download the image to our registry, scan it for any viruses or threats, after successful scan we can deploy the pod or else we cannot. Simple example would be AWS ECR supports the image scanning, we can upload the image than it scans and for scan results can be shared on a SNS topic where we can run a custom subscriber to handle the scan failures.

- We can also include a Tenant-id in a JET token when we use this system as a multi tenant one and we store the docker image with that tenant id so when they want to run the pod we can make sure someone who provided the image can only run no one else based on the tenant id.

- In production we will definetly use TLS/HTTPS from client to server communication so in data in transist will always be encrypted. We can have a separate section for the secret in the pod Spec and those values we can encrypt it with a key (KMS key for example) and store it in a s3 bucket or cloud bucket. Here we can utilize a tool called KSOPS which can encrypt and decrypt such things and the format can be a kubernetes secret format. You can write secrets to a file which has the format of a kubernetes secret object and than encrypt it with KSOPS tool, which will ensure only values are encrypted and rest of the format stays as it is, so when we want to create actual secret on the cluster we just need to decrypt and apply.

- One more approach i can think here is we can create a KMS key using which anyone can encrypt their data and they can only encrypt not decrypt. We can share that key with customer to encrypt the secret and than upload the secret file to us, which only our system has decrypt access. This ensures double encryption during the transport. We can think of one key per customer but that won't make much difference as we are using one pod-launcher app for all the customers.

2. Scalability
What sort of things should be considered to take this service into scale? Imagine thousands of users, with tens of thousands of services.

- <b>ANSWER: </b> If we want to run this system on a scale, i would choose a worker based system, where API takes a job to create a pod, or view status and than it puts the details to the queue, workers picks up the task from queue and puts them to a centalized storage, probably a NoSQL db as the structure would be really hard to maintain for such tasks and than API can fetch results from there and share it with the users.
- We can scale the main API server based on the number of request coming in order to serve the users smoothly and at the same time we can scale worker pods based on the number of messages in the queue. This we can achieve using KEDA(Kubernetes Event Driven Autoscaler).
- We can group workers based on the tasks they are doing so that we can make scaling desicions better and that saves the cost as well.

3.  UX
Users would likely need good insights about their running service, e.g. data such as logs, health checks, etc. How would you approach this?

- <b>ANSWER: </b> We can collect 2 types of data here, metrics and logs. I am making one assumption here that each customer runs their pods in their own namespace, which has tenant-id added by us in the namespace name.

- For metrics:
  - We can deploy one prometheus instance per namespace to do better isolation of the metriccs being collected and that will have tenant_id label we can extract from the namespace name.
  - We can create dashboard in Grafana where they can visualize their metrics like, cpu-memory usage, pod restart count and many more. Dahsboards in Grafana can be created using JSON file where we can hardcode the tenant-id in the query and for each tenant we can create a separate folder in grafana to store those dashboards. This ensures that we can create same dashboard via code just need to change the tenant-id in grafana for each tenant. 
  - Use OAuth, LDAP or SAML to assign each tenant user only to their folder and give them read-only access. This setup ensures that only users can see the data of their deployment and not of any other.

- For logs:
  - We can use fluentbit or fluentd running as a daemonset to collect the logs from stdout and send those to Loki.
  - We can configure the loki to store logs with tenant-id labels which we can again fetch from the namespace name.
  - Deploy the loki in multi tenant mode(By setting up auth_enabled: true) and enforce tenant header. (X-Scope-OrgID).
  - In Grafana create a loki data source per tenant with fixed `X-Scope-OrgID`. This again can be automated via code.
  - Same way create the dashboards using the datasource created in the previous step in the same folder as metrics one so that access level setup is already handled ther.

This way we can expose the information with isolating the data between tenants.

