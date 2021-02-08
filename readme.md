# Financial Portfolio Management System

![GitHub top language](https://img.shields.io/github/languages/top/CleitonAlmeida/financial-portfolio-management-system)

I'm IT man, but I like to understand about the financial market (stocks, options, REITs and so on). I am far from financial freedom, but I already try to save some money, making use of ClubeFii, StatusInvest, and similar applications, and I missed an application that would give me total control over the information of my investment portfolio, a system that can consolidate from treasury direct applications, brazilian stocks to foreign stocks, REITs and ETFs. With this I had the idea to start this project, besides controlling the finances, it also allows me to learn about the novelties of web development. I will be very grateful if you want to contribute in any way (either with code or just by call out for code improvements and use of standards...)

Sou da TI, porem gosto muito de entender sobre o mercado financeiro (acoes, opcoes, REITs e afins). Estou bem longe da liberdade financeira, porem ja tento juntar uma graninha, fazendo uso de aplicacoes tipo ClubeFii, StatusInvest, e afins, e sentia falta de uma aplicacao que me desse total controle sobre as informacoes da minha carteira de investimentos, e um sistema que consiga consolidar desde aplicacoes do Tesouro Direto, Acoes brasileiras ate acoes estrangeiras, REITs e ETFs. Com isso tive a ideia de iniciar este projeto, para alem de controlar as financas, tambem me permitir aprender sobre as novidades do desenvolvimento web. Serei muito grato caso queira contribuir de alguma forma (seja com codigo ou apenas puxando a minha orelha pra melhorias de codigo e uso de padroes...)

---

## Prerequisites

* Python 3.8
* PostgreSQL
* Docker
---

## Installation

Change the .env according to the model present in the repository

Use the package manager [pipenv](https://pypi.org/project/pipenv/) to install.

```sh
$ git clone https://github.com/CleitonAlmeida/financial-portfolio-management-system
$ cd financial-portfolio-management-system
$ pipenv install
$ pipenv shell
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsu
$ gunicorn finance.wsgi:application -b 0.0.0.0:8000 --log-file -
```
---
Or using [docker](https://www.docker.com/get-started)

```sh
$ git clone https://github.com/CleitonAlmeida/financial-portfolio-management-system
$ cd financial-portfolio-management-system
$ docker-compose --file=docker-compose-dev.yml up
```

You can now go to [http://localhost:8000](http://localhost:8000)

---
Or on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/CleitonAlmeida/financial-portfolio-management-system)

---

## Built With

* [Python 3.8](https://www.python.org/doc/)
* [Django 3.1.3](https://docs.djangoproject.com/en/3.1/)
* [Celery - Task Queue](https://docs.celeryproject.org/en/stable/)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---
