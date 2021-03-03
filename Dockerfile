FROM python:3.8.7-slim-buster
RUN apt update

COPY . /code
WORKDIR /code

RUN pip install pipenv \
  && pipenv install $(test "$DJANGO_ENV" == production || echo "--dev") --deploy --system --ignore-pipfile
