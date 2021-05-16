FROM python:3.7
ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code
ADD requirements.txt /code/

RUN pip3 install --upgrade pip==21.0.1 \
    && pip3 install -r requirements.txt

ADD . /code/
