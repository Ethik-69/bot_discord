FROM python:3.7-alpine3.10

COPY ./ /home/app/

WORKDIR /home/app/

RUN apk update && apk add build-base openssl-dev libffi-dev rethinkdb && rm -rf /var/cache/apk/*
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install discord -t ./lib/

ENTRYPOINT ["python", "bot.py"]
