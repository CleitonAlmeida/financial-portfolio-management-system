from django.core import exceptions
from finance.celery import app
from celery.schedules import crontab

@app.task
def add(x, y):
    return x + y

def refresh_current_price(ticker):
    app.send_task('refresh_current_price', args=[ticker])

def refresh_assets_prices():
    from portfolio.services import refresh_current_price as refresh_price
    from portfolio.selectors import get_assets_types, get_active_assets
    for t in get_assets_types():
        assets = get_active_assets(type_investment=t)
        for asset in assets:
            app.send_task('refresh_current_price', args=[asset.ticker])
