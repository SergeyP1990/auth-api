# pull official base image
FROM python:3.9.7-slim-buster

# set work directory
WORKDIR /usr/src/tests

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# copy project
COPY . .


ENTRYPOINT ["sh", "-c", "python3 main.py \
      && pytest /usr/src/tests/src -v"]
