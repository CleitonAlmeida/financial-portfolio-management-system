from django.core import exceptions
from finance.celery import app
"""from portfolio.services import (
    refresh_current_price as refresh_price
)
from portfolio.selectors import (
    get_assets_types,
    get_active_assets
)"""
from celery.schedules import crontab

@app.task
def add(x, y):
    return x + y

@app.task
def refresh_current_price(ticker):
    from portfolio.services import refresh_current_price as refresh_price
    try:
        refresh_price(ticker=ticker)
    except exceptions.ObjectDoesNotExist:
        print('ObjectDoesNotExist')

@app.task
def refresh_assets_prices():
    from portfolio.services import refresh_current_price as refresh_price
    from portfolio.selectors import get_assets_types, get_active_assets
    for t in get_assets_types():
        assets = get_active_assets(type_investment=t)
        for asset in assets:
            try:
                refresh_price(ticker=asset.ticker)
            except exceptions.ObjectDoesNotExist:
                print('ObjectDoesNotExist')
