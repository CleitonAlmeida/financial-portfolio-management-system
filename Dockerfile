FROM python:3.9.4-slim-buster
RUN apt update

COPY . /code
WORKDIR /code

RUN pip install --upgrade poetry

RUN poetry export --without-hashes --with-credentials -f requirements.txt > requirements.txt

RUN pip install -r requirements.txt