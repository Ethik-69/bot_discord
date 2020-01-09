# Bot Discord

## main app

docker build -t bot_first_try:0.1 .
docker run --name main_bot -v "$PWD/app/log:/home/app/log" -d -p 28015:28015 bot_first_try:0.1

https://docs.docker.com/engine/reference/commandline/logs/
docker logs {container_id} --tail=all -f

## DB

https://hub.docker.com/_/rethinkdb?tab=description

docker run --name some-rethink -v "$PWD/rethinkdb_data:/data/rethinkdb_data" -d -p 8080:8080 -p 29015:29015 -p 28015:28015 rethinkdb

$BROWSER "http://$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' some-rethink):8080"

## Kube

https://medium.com/@yzhong.cs/getting-started-with-kubernetes-and-docker-with-minikube-b413d4deeb92

### Usefull cmd

- tail:  
`watch command x`

- Get replicaset:  
`kubectl get rs`

- get pods:  
`kubectl get pods`

- get deployment:  
`kubectl get deployments`

- get all:  
`kubectl get all`

- kube man:  
`kubectl api-resources`
`kubectl explain resources.tarace.boulba.beach`

- run dashboard:  
`minikube dashboard`

- connect into pod:  
`kubectl exec -it {pod_name} -- /bin/sh`

- create secret for docker:  
`kc create secret docker-registry docker-private --docker-server=https://index.docker.io/v1/ --docker-username=ethik69 --docker-password=xxxxxx`


- Archi viewer:  
https://github.com/hjacobs/kube-ops-view
