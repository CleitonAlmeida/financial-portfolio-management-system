from django.contrib.auth.models import User
from django.db.models import (
    Sum,
    F,
    Case,
    When
)
from portfolio.models import (
    Portfolio,
    Transaction,
    Asset,
    AssetType,
    PortfolioConsolidated,
    PortfolioAssetConsolidated
)
from portfolio.constants import (
    TypeTransactions
)
from typing import Iterable

def get_portfolios(
    *,
    fetched_by: User,
    filters=None
) -> Iterable[Portfolio]:
    filters = filters or {}
    filters['owner'] = fetched_by
    return Portfolio.objects.filter(**filters).distinct()

def get_transactions(
    *,
    portfolio: Portfolio,
    filters=None
) -> Iterable[Transaction]:
    filters = filters or {}
    qs = Transaction.objects.filter(portfolio=portfolio)
    return qs.filter(**filters)

def get_assets_types(
    *,
    filters=None
) -> Iterable[AssetType]:
    filters = filters or {}
    qs = AssetType.objects.filter()
    return qs.filter(**filters)

def get_assets(
    *,
    filters=None
) -> Iterable[Asset]:
    filters = filters or {}
    qs = Asset.objects.filter()
    return qs.filter(**filters)

def get_stocks(
    *,
    filters=None
) -> Iterable[Asset]:
    filters = filters or {}
    qs = Asset.objects.filter(type_investment__name='STOCK')
    return qs.filter(**filters)

def get_active_assets(
    *,
    type_investment: AssetType,
    filters=None
) -> Iterable[Asset]:
    qs = PortfolioAssetConsolidated.objects.filter(
        asset__type_investment=type_investment)
    qs = qs.values('asset').distinct('asset')
    return Asset.objects.filter(pk__in=[q['asset'] for q in qs])

def get_fiis(
    *,
    filters=None
) -> Iterable[Asset]:
    filters = filters or {}
    qs = Asset.objects.filter(type_investment__name='FII')
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

#NCZP => No Consider Zeroed Positions
def get_transactions_asset_nczp(
    *,
    portfolio:Portfolio,
    asset:Asset,
    filters=None
) -> Iterable[Transaction]:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('''
        WITH transaction_dates
             AS (SELECT DISTINCT transaction_date date_t
                 FROM   portfolio_transaction
                 WHERE  portfolio_id = %s
                        AND asset_id = %s)
        SELECT td.date_t,
               Sum(CASE
                     WHEN pt.type_transaction = \''''+
                        TypeTransactions.BUY.value +
                        '''\' THEN pt.quantity * -1
                     WHEN pt.type_transaction = \''''+
                        TypeTransactions.SELL.value +
                        '''\' THEN pt.quantity
                     ELSE NULL
                   END) AS qty
        FROM   portfolio_transaction pt,
               transaction_dates td
        WHERE  pt.portfolio_id = %s
               AND pt.asset_id = %s
               AND pt.transaction_date <= td.date_t
        GROUP  BY td.date_t
        HAVING Sum(CASE
                     WHEN pt.type_transaction = \''''+
                        TypeTransactions.BUY.value +
                        '''\' THEN pt.quantity * -1
                     WHEN pt.type_transaction = \''''+
                        TypeTransactions.SELL.value + 
                        '''\' THEN pt.quantity
                     ELSE NULL
                   END) = 0
        ORDER  BY td.date_t DESC
        ''', [portfolio.pk, asset.pk, portfolio.pk, asset.pk]);
        row = cursor.fetchone()
        #print('LEN %s', len(row))
    if row:
        qs = get_transactions_asset(portfolio=portfolio, asset=asset)
        return qs.filter(transaction_date__gt=row[0])
    else:
        return get_transactions_asset(portfolio=portfolio, asset=asset)

def get_all_assets_portfolio(
    *,
    portfolio:Portfolio,
    filters=None
) -> Iterable[Asset]:
    qs = get_transactions(portfolio=portfolio, filters=filters)
    qs = qs.values('asset').distinct('asset')
    return Asset.objects.filter(pk__in=[q['asset'] for q in qs])

def get_current_assets_portfolio(
    *,
    portfolio:Portfolio,
    filters=None
) -> Iterable[Asset]:
    qs = get_transactions(portfolio=portfolio, filters=filters)
    qs = qs.annotate(
        qty=Case(
            When(type_transaction=TypeTransactions.BUY.value, then=(
                F('quantity')
            )),
            When(type_transaction=TypeTransactions.SELL.value, then=(
                F('quantity')*-1
            )),
        )
    )
    qs = qs.values('asset').annotate(
        current_qty=Sum('qty')
    ).filter(current_qty__gt=0)
    return Asset.objects.filter(pk__in=[q['asset'] for q in qs])

def get_assets_consolidated(
    *,
    portfolio:Portfolio,
    filters=None
) -> Iterable[PortfolioAssetConsolidated]:
    qs = PortfolioAssetConsolidated.objects.filter(portfolio=portfolio)
    filters = filters or {}
    return qs.filter(**filters)

def get_portfolio_consolidated(
    *,
    portfolio:Portfolio,
    filters=None
) -> Iterable[PortfolioConsolidated]:
    qs = PortfolioConsolidated.objects.filter(portfolio=portfolio)
    filters = filters or {}
    return qs.filter(**filters)
