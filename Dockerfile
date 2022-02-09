# pull official base image
FROM python:3.9.0-alpine

# set work directory
WORKDIR /server

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev python3-dev libffi-dev openssl-dev build-base

COPY . .

EXPOSE 5000

# RUN ls -la server/

# ENTRYPOINT ["sh", "/server/docker-entrypoint.sh"]

RUN pip install -r requirements.txt

RUN ["chmod", "+x", "server/docker-entrypoint.sh"]