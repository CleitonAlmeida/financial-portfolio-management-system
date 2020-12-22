from django.contrib.auth.models import User
from portfolio.models import (
    Portfolio,
    Transaction,
    Asset
)
from typing import Iterable

def get_portfolios(
    *,
    fetched_by: User
) -> Iterable[Portfolio]:
    return Portfolio.objects.filter(owner=fetched_by)

def get_transactions(
    *,
    portfolio: Portfolio,
    filters=None
) -> Iterable[Transaction]:
    filters = filters or {}
    qs = Transaction.objects.filter(portfolio=portfolio)
    return qs.filter(**filters)

#Need test
def get_transactions_user(
    *,
    user: User,
    filters=None
) -> Iterable[Transaction]:
    filters = filters or {}
    qs = Transaction.objects.filter(
        portfolio__in=get_portfolios(
            fetched_by=user
        ))
    return qs.filter(**filters)

def get_fii_transactions(
    *,
    portfolio: Portfolio,
    filters=None
) -> Iterable[Transaction]:
    qs = get_transactions(portfolio=portfolio, filters=filters)
    return qs.filter(type_investment__name='FII')

#Need test
def get_fii_transactions_user(
    *,
    user: User
) -> Iterable[Transaction]:
    filters = {
        'type_investment__name': 'FII'
    }
    return get_transactions_user(user=user, filters=filters)

#Need test
def get_stock_transactions_user(
    *,
    user: User
) -> Iterable[Transaction]:
    filters = {
        'type_investment__name': 'STOCK'
    }
    return get_transactions_user(user=user, filters=filters)

def get_stock_transactions(
    *,
    portfolio: Portfolio,
    filters=None
) -> Iterable[Transaction]:
    qs = get_transactions(portfolio=portfolio, filters=filters)
    return qs.filter(type_investment__name='STOCK')

def get_transactions_asset(
    *,
    portfolio:Portfolio,
    asset:Asset,
    filters=None
) -> Iterable[Transaction]:
    qs = get_transactions(portfolio=portfolio, filters=filters)
    return qs.filter(asset=asset)
