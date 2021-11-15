# syntax=docker/dockerfile:1
FROM ubuntu:focal-20210921

WORKDIR /app

ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y python3.8
RUN apt-get install -y python3-distutils python3-pip python3-apt

RUN pip3 install pipenv
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --system

COPY . .

CMD ["python3", "main.py"]
