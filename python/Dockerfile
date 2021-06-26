FROM python:3.8.5
ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code
ADD requirements.txt /code/

RUN pip3 install --upgrade pip==21.0.1 \
    && pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential && apt-get install -y gettext libgettextpo-dev

ADD . /code/
