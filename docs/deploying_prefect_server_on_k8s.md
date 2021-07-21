# Deploying prefect server on kubernetes cluster (GKE) and running a multiple file flow
In this article we will be deploying a prefect server on kubernetes (GKE) and running a basic, but multiple file flow.

## Before we begin:
* Make sure that your kubernetes cluster is created and that your kubectl is configured to use it.
* Make sure you are using `Python 3.8` not `Python 3.9` (it is not supported yet).
* Make sure you have a postgresql database available
* You have prefect cli installed
* You have a gocke registry configured and your local docker is authorized to add to it

## A persistent database.
Even though prefect server Helm chart comes with a postgresql, it is deployed on kubernetes. So you can not really call it persistent, and all the data it stores will be occasionally wiped. This is nice for testing but horrible for production. We need an external database. For our example our database would be at Google Cloud SQL, but you can deploy the database however you choose. Just make sure it is externally accessible. These would be our database connection credantials:
```json
database: prefect
username: my_username
password: my_password
host: 111.111.111.111
port: 5432
```
Also you need to run the following sql request on the database:
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
SET TIME ZONE 'UTC';
```
## Creating a secret
We do not want to store our password for connection to the database in a file. We will use a kubernetes secret. Run
`kubectl create secret generic prefect-server-database-password --from-literal=postgresql-password=my_password`
(my_password is a password for your databases connection)
## Deploying prefect server:
We are gong to use a helm chart to deploy our server, but because we have an external database, we need to edit the default configurations. We will need to download `values.yaml`
`helm show values prefecthq/prefect-server | >> charts/prefect-server/values.yaml`
Now we need to edit the values in `charts/prefect-server/values.yaml` Set under the postgresql section:
``` yaml
postgresqlDatabase: prefect
postgresqlUsername: my_user
existingSecret: prefect-server-database-password
servicePort: 5432
externalHostname: 111.111.111.111
useSubChart: false
```

Now lets deploy it:
`helm install -f ../../charts/prefect-server/values.yaml prefect-server prefecthq/prefect-server`

From here on lets remember somthing:
`$UI_HOST` is a url of your prefect UI. To get it run:
```bash
 UI_HOST=$( \
    kubectl get svc \
    --namespace default \
    --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}" \
    prefect-server-ui \
  ) \
  && echo "UI available at: http://$UI_HOST:8080
```
`$API_HOST` is a url of your graphql server. To get it run:
```bash
API_HOST=$( \
    kubectl get svc \
    --namespace default \
    --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}" \
    prefect-server-apollo \
  ) \
  && echo "API available at: http://$API_HOST:4200/graphql"
```
You need to set in your `~/.prefect/config.toml`
```toml
[server]
  host = "http://$API_HOST:4200/graphql
```
run
`prefect backend server`
and create a tenant:
`prefect server create-tenant --name my_tenant --slug my_tenant`

Now open UI  `http://$UI_HOST:8080` and go through the steps there.
You are all set - your server is deployed.

## Deploying an agent
We will be deploying an agent on the same k8s cluster as the server. If you want it to be on a different cluster, just connect your `kubectl` to the new cluster.
`prefect agent kubernetes install --api http://$API_HOST:4200/graphql --rbac | kubectl apply -f -`
Don't forget to change `$API_HOST` to your graphql url.

You need additional permissions for the agent to run correctly. Run `kubectl edit role prefect-agent-rbac`
and edit `rules` section to be:
```yaml
rules:
- apiGroups:
  - batch
  - extensions
  resources:
  - jobs
  verbs:
  - '*'
- apiGroups:
  - ""
  resources:
  - events
  - pods
  #ADD THIS
  - pods/log
  - services 
  verbs:
  - '*'
- apiGroups:
  - policy
  resources:
  - poddisruptionbudgets
  verbs:
  - '*'
```
Now your agent is ready.