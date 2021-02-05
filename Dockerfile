FROM python:3.8.7-slim-buster
RUN apt update

COPY . /code
WORKDIR /code

RUN apt-get install -y gcc
RUN apt install -y libcurl4-openssl-dev libssl-dev
#RUN pipenv lock
#RUN pipenv sync
#RUN pipenv shell

RUN pip install pipenv \
  && pipenv install $(test "$DJANGO_ENV" == production || echo "--dev") --deploy --system --ignore-pipfile
