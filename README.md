# Bot Discord

## main app

docker build -t bot_first_try:0.1 .
docker run --name main_bot -d ethik69/bot_discord:latest

## DB

[RethinkDB docker](https://hub.docker.com/_/rethinkdb?tab=description)

`docker run --name some-rethink -v "$PWD/rethinkdb_data:/data/rethinkdb_data" -d -p 8080:8080 -p 29015:29015 -p 28015:28015 rethinkdb`

`$BROWSER "http://$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' some-rethink):8080"`

## Kube

[Tuto docker with kube](https://medium.com/@yzhong.cs/getting-started-with-kubernetes-and-docker-with-minikube-b413d4deeb92)

## Docker

`docker build -t ethik69/bot_discord:0.1 .`
`docker push ethik69/bot_discord:tagname`
`for i in $(docker ps -a | awk 'NR != 1 {print $1}'); do docker stop $i && docker rm $i; done`
`for i in $(docker images | awk 'NR != 1 {print $3}'); do docker rmi $i; done`

[Docker cmd line ref](https://docs.docker.com/engine/reference/commandline/logs/)  
`docker logs {container_id} --tail=all -f`

## gRPC

[Site](https://grpc.io)

### Usefull cmd

- tail:  
`watch command x`

- Get replicaset:  
`kubectl get rs`

- get pods:  
`kubectl get pods`

- get deployment:  
`kubectl get deployments`

- force kill smth:
`kc delete smth xxxxxxxxxx --force --grace-period=0`

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

- open viewer:
`kubectl port-forward service/kube-ops-view 8081:80`

- Archi viewer:  
[github](https://github.com/hjacobs/kube-ops-view)

- Set dep image
`kubectl set image deployment/nginx nginx=nginx:1.9.1`
`kubectl set image deployment/dep_namee container_name=image_name:image_tag`

### Weavescope

`kubectl apply -f "https://cloud.weave.works/k8s/scope.yaml?k8s-version=$(kubectl version | base64 | tr -d '\n')"`
`kubectl port-forward -n weave "$(kubectl get -n weave pod --selector=weave-scope-component=app -o jsonpath='{.items..metadata.name}')" 4040`
`kubectl delete -f "https://cloud.weave.works/k8s/scope.yaml?k8s-version=$(kubectl version | base64 | tr -d '\n')"`


### main

`minikube start/stop`
`kubectl port-forward -n weave "$(kubectl get -n weave pod --selector=weave-scope-component=app -o jsonpath='{.items..metadata.name}')" 4040`


## TODO

### Bot:

=> Add channel in DB  
=> Add audio managment  

### RethinkDB:
=> secu: auth key  
=> Config retry when conn fail  

## Source

https://github.com/tensor-programming/docker_grpc_chat_tutorial