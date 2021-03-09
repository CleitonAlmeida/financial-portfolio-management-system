from django.core import exceptions
from finance.celery import app
from celery.schedules import crontab

def refresh_current_price(ticker):
    app.send_task('refresh_current_price', args=[ticker])

def refresh_assets_prices():
    from portfolio.selectors import get_assets_types, get_active_assets
    for t in get_assets_types():
        assets = get_active_assets(type_investment=t)
        for asset in assets:
            refresh_current_price(asset.ticker)
