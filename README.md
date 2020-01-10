# Bot Discord

## main app

docker build -t bot_first_try:0.1 .
docker run --name main_bot -d ethik69/bot_discord:latest

https://docs.docker.com/engine/reference/commandline/logs/
docker logs {container_id} --tail=all -f

## DB

https://hub.docker.com/_/rethinkdb?tab=description

docker run --name some-rethink -v "$PWD/rethinkdb_data:/data/rethinkdb_data" -d -p 8080:8080 -p 29015:29015 -p 28015:28015 rethinkdb

$BROWSER "http://$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' some-rethink):8080"

## Kube

https://medium.com/@yzhong.cs/getting-started-with-kubernetes-and-docker-with-minikube-b413d4deeb92

## Docker

`docker build -t ethik69/bot_discord:0.1 .`
`docker push ethik69/bot_discord:tagname`
`for i in $(docker ps -a | awk 'NR != 1 {print $1}'); do docker stop $i && docker rm $i; done`
`for i in $(docker images | awk 'NR != 1 {print $3}'); do docker rmi $i; done`

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

- Get minikube ip:
`minikube ip`

- Archi viewer:  
https://github.com/hjacobs/kube-ops-view
