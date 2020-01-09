# docker build -t ethik69/bot_discord:0.1 .
# docker push ethik69/bot_discord:tagname
# for i in $(docker ps -a | awk 'NR != 1 {print $1}'); do docker stop $i && docker rm $i; done
# for i in $(docker images | awk 'NR != 1 {print $3}'); do docker rmi $i; done
FROM python:3.9.0a1-alpine3.10

COPY ./app/ /home/app/

WORKDIR /home/app/

RUN apk update && apk add build-base openssl-dev libffi-dev && rm -rf /var/cache/apk/*
RUN pip install -r requirements.txt
RUN pip install discord -t ./lib/

ENTRYPOINT ["python", "bot.py"]
