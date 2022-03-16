# pull official base image
FROM python:3.9

# set work directory
WORKDIR /usr/src/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# copy project
COPY . /usr/src/
CMD gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - "wsgi_app:application"
