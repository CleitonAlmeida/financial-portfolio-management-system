from django.contrib.auth.models import User
from django.core import exceptions
from django.utils import timezone
from django.db import transaction
from decouple import config
from django.db.models import (
    Sum,
    F,
    Q,
    Case,
    When,
    Model
)
from django.http import Http404
from portfolio.models import (
    Portfolio,
    AssetType,
    Asset,
    Transaction,
    PortfolioConsolidated,
    PortfolioAssetConsolidated
)
from portfolio.selectors import (
    get_transactions_asset,
    get_transactions,
    get_current_assets_portfolio,
    get_all_assets_portfolio,
    get_transactions_asset_nczp,
    get_portfolio_consolidated,
    get_assets_consolidated,
    get_assets
)
from portfolio.constants import (
    TypeTransactions,
    CurrencyChoices,
    StockBrokerChoices
)
from typing import (
    Optional,
    Union,
    NewType,
    Iterable,
    Literal
)
from decimal import Decimal
import datetime
from enum import Enum
import requests, json, re


def _test_permissions(
    *,
    user: User,
    permission: str,
    object: Optional[Model] = None
) -> None:
    if object is not None:
        app_label = object._meta.app_label
        if(hasattr(object, 'test_permission_user')):
            has_permission = object.test_permission_user(user=user)
            if not has_permission:
                #print("has_permission object %s %s", permission, has_permission)
                raise exceptions.PermissionDenied
        else:
            raise exceptions.PermissionDenied
    else:
        app_label = 'portfolio'

    has_permission = user.has_perm(app_label+'.'+permission)
    if not has_permission:
        raise exceptions.PermissionDenied

def create_portfolio(
    *,
    id: Optional[int] = 0,
    owner: User,
    name: str,
    desc_1: str = None,
) -> Portfolio:
    _test_permissions(user=owner,permission='add_portfolio')
    data = {}
    data['owner'] = owner
    data['name'] = name
    data['desc_1'] = desc_1

    try:
        portfolio = Portfolio.objects.get(pk=id)
        Portfolio.objects.filter(pk=id).update(**data)
        portfolio.refresh_from_db()
    except exceptions.ObjectDoesNotExist:
        portfolio = Portfolio.objects.create(**data)
    return portfolio

def task_refresh_price(
    *,
    ticker: str
):
    from portfolio.tasks import refresh_current_price as refresh
    refresh.delay(ticker)

def task_refresh_all_prices():
    from portfolio.tasks import refresh_assets_prices
    refresh_assets_prices.delay()

def get_or_create_asset_type(
    *,
    name: str
) -> AssetType:
    try:
        asset_type = AssetType.objects.get(name=name)
    except exceptions.ObjectDoesNotExist:
        asset_type = AssetType.objects.create(
            name=name,
        )
    return asset_type

def create_asset(
    *,
    id: Optional[int] = 0,
    ticker: str,
    type_investment: Optional[AssetType] = None,
    name: str = None,
    currency: str=CurrencyChoices.REAL.value,
    current_price: Optional[Decimal] = 0.0,
    desc_1: str = None,
    desc_2: str = None,
    desc_3: str = None,
) -> Asset:
    filter = {'ticker': ticker}
    if type_investment is not None and type(type_investment) == str:
        type_investment = get_or_create_asset_type(name=type_investment)
        filter['type_investment'] = type_investment
    if id:
        filter['pk'] = id

    data = {}
    asset_info = get_ticker_info(ticker=ticker)

    data['ticker'] = ticker
    data['type_investment'] = type_investment
    data['name'] = name or asset_info.get('longname')
    data['currency'] = currency
    data['current_price'] = current_price
    data['desc_1'] = desc_1 or asset_info.get('shortname')
    data['desc_2'] = desc_2 or asset_info.get('symbol')
    data['desc_3'] = desc_3

    try:
        asset = Asset.objects.get(**filter)
        Asset.objects.filter(**filter).update(**data)
        asset.refresh_from_db()
    except exceptions.ObjectDoesNotExist:
        asset = Asset.objects.create(**data)
    task_refresh_price(ticker=ticker)
    return asset


def refresh_current_price(
    *,
    ticker: str
) -> bool:
    price = get_current_price(ticker=ticker)
    if price:
        Asset.objects.filter(ticker=ticker).update(
            current_price=price,
            last_update=timezone.now()
        )
        return True
    return False

def create_transaction(
    *,
    id: Optional[int] = 0,
    portfolio: Portfolio,
    type_transaction: str,
    type_investment: Union[str,AssetType] = None,
    transaction_date: datetime = timezone.now(),
    asset: Union[str, Asset],
    quantity: Union[int,float,Decimal],
    unit_cost: Union[int,float,Decimal],
    currency: str=CurrencyChoices.REAL.value,
    other_costs: Union[int,float,Decimal] = Decimal('0.0'),
    desc_1:str = None,
    desc_2:str = None,
    stockbroker: str = StockBrokerChoices.RI.value,
) -> Transaction:

    params = {'ticker': asset}
    if isinstance(type_investment, AssetType):
        type_investment = type_investment
        params['type_investment'] = type_investment
    elif isinstance(type_investment, str):
        type_investment = get_or_create_asset_type(name=type_investment)
        params['type_investment'] = type_investment
    else:
        type_investment = None

    if isinstance(asset, str):
        asset = get_assets(filters=params)[0]

    data = {}
    data['portfolio'] = portfolio
    data['type_transaction'] = type_transaction
    data['transaction_date'] = transaction_date
    data['asset'] = asset
    data['type_investment'] = asset.type_investment
    data['quantity'] = quantity
    data['unit_cost'] = unit_cost
    data['currency'] = currency
    data['other_costs'] = other_costs
    data['desc_1'] = desc_1
    data['desc_2'] = desc_2
    data['stockbroker'] = stockbroker
    data['consolidated'] = False

    try:
        transaction = Transaction.objects.get(pk=id)
        Transaction.objects.filter(pk=id).update(**data)
        transaction.refresh_from_db()
    except exceptions.ObjectDoesNotExist:
        transaction = Transaction.objects.create(**data)
    task_refresh_price(ticker=asset.ticker)

    portfolio.consolidated = False
    portfolio.save()
    task_refresh_price(ticker=asset.ticker)
    return transaction

def create_fii_transaction(
    *,
    user: User,
    id: Optional[int] = 0,
    portfolio: Portfolio,
    type_transaction: str,
    transaction_date: datetime = timezone.now(),
    asset: Union[str, Asset],
    quantity: Union[int,float,Decimal],
    unit_cost: Union[int,float,Decimal],
    currency: str=CurrencyChoices.REAL.value,
    other_costs: Union[int,float,Decimal] = Decimal('0.0'),
    desc_1:str = None,
    desc_2:str = None,
    stockbroker: str = StockBrokerChoices.RI.value,
) -> Transaction:
    _test_permissions(user=user,permission='add_fiitransaction')
    if isinstance(asset, str):
        asset = get_assets(filters={'ticker': asset})[0]

    if asset.type_investment.name != 'FII':
        raise exceptions.ValidationError('Invalid Asset Type')

    return create_transaction(
        id=id,
        portfolio=portfolio,
        type_transaction=type_transaction,
        type_investment='FII',
        transaction_date=transaction_date,
        asset=asset,
        quantity=quantity,
        unit_cost=unit_cost,
        currency=currency,
        other_costs=other_costs,
        desc_1=desc_1,
        desc_2=desc_2,
        stockbroker=stockbroker
    )

def create_stock_transaction(
    *,
    user: User,
    id: Optional[int] = 0,
    portfolio: Portfolio,
    type_transaction: str,
    transaction_date: datetime = timezone.now(),
    asset: Union[str, Asset],
    quantity: Union[int,float,Decimal],
    unit_cost: Union[int,float,Decimal],
    currency: str=CurrencyChoices.REAL.value,
    other_costs: Union[int,float,Decimal] = Decimal('0.0'),
    desc_1:str = None,
    desc_2:str = None,
    stockbroker: str = StockBrokerChoices.RI.value,
) -> Transaction:
    _test_permissions(user=user,permission='add_stocktransaction')

    if isinstance(asset, str):
        asset = get_assets(filters={'ticker': asset})[0]

    if asset.type_investment.name != 'STOCK':
        raise exceptions.ValidationError('Invalid Asset Type')

    return create_transaction(
        id=id,
        portfolio=portfolio,
        type_transaction=type_transaction,
        type_investment='STOCK',
        transaction_date=transaction_date,
        asset=asset,
        quantity=quantity,
        unit_cost=unit_cost,
        currency=currency,
        other_costs=other_costs,
        desc_1=desc_1,
        desc_2=desc_2,
        stockbroker=stockbroker
    )

def get_qty_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.annotate(
        qty=Case(
            When(type_transaction=TypeTransactions.BUY.value, then=F('quantity')),
            When(type_transaction=TypeTransactions.SELL.value, then=F('quantity')*-1),
        )
    )
    qs = qs.aggregate(Sum(F('qty')))
    return qs['qty__sum'] if qs['qty__sum'] is not None else Decimal(0)

def get_total_cost_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.annotate(
        qty=Case(
            When(type_transaction=TypeTransactions.BUY.value, then=(
                ((F('unit_cost') * F('quantity')) + F('other_costs'))*-1
            )),
            When(type_transaction=TypeTransactions.SELL.value, then=(
                (F('unit_cost') * F('quantity')) - F('other_costs')
            )),
        )
    )
    qs = qs.aggregate(Sum(F('qty')))

    return qs['qty__sum'] if qs['qty__sum'] is not None else Decimal(0)

def get_total_buy_transactions(
    *,
    portfolio: Portfolio,
    filters=None
) -> Decimal:
    filters = filters or {}
    filters['type_transaction'] = TypeTransactions.BUY.value
    qs = get_transactions(portfolio=portfolio, filters=filters)
    qs = qs.annotate(
        total=(F('unit_cost') * F('quantity')) - F('other_costs')
    )
    qs = qs.aggregate(Sum(F('total')))

    return qs['total__sum'] if qs['total__sum'] is not None else Decimal(0)

def get_total_sell_transactions(
    *,
    portfolio: Portfolio,
    filters=None
) -> Decimal:
    filters = filters or {}
    filters['type_transaction'] = TypeTransactions.SELL.value
    qs = get_transactions(portfolio=portfolio, filters=filters)
    qs = qs.annotate(
        total=(F('unit_cost') * F('quantity')) - F('other_costs')
    )
    qs = qs.aggregate(Sum(F('total')))

    return qs['total__sum'] if qs['total__sum'] is not None else Decimal(0)

def get_total_dividend_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.filter(type_transaction=TypeTransactions.DIVIDEND.value)
    qs = qs.annotate(div=(F('unit_cost') * F('quantity')) - F('other_costs'))
    qs = qs.aggregate(Sum(F('div')))
    return qs['div__sum'] if qs['div__sum'] is not None else Decimal(0)

def get_total_dividend_asset_nczp(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset_nczp(portfolio=portfolio, asset=asset)
    qs = qs.filter(type_transaction=TypeTransactions.DIVIDEND.value)
    qs = qs.annotate(div=(F('unit_cost') * F('quantity')) - F('other_costs'))
    qs = qs.aggregate(Sum(F('div')))
    return qs['div__sum'] if qs['div__sum'] is not None else Decimal(0)

def get_operation_cost_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.aggregate(total_cost=Sum('other_costs'))
    return qs['total_cost'] if qs['total_cost'] is not None else Decimal(0)

def get_operation_cost_asset_nczp(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset_nczp(portfolio=portfolio, asset=asset)
    qs = qs.aggregate(total_cost=Sum('other_costs'))
    return qs['total_cost'] if qs['total_cost'] is not None else Decimal(0)

def get_avg_price_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qty = get_qty_asset(portfolio=portfolio, asset=asset)
    if qty > 0:
        total = get_avg_purchase_price_nczp(portfolio=portfolio, asset=asset)
        return total/qty
    else:
        return 0

def get_avg_purchase_price(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.filter(type_transaction = TypeTransactions.BUY.value)
    qs = qs.aggregate(
            avg_pp=Sum((F('unit_cost') * F('quantity')) + F('other_costs'))/
                Sum(F('quantity'))
        )
    return qs['avg_pp'] if qs['avg_pp'] is not None else Decimal(0)

def get_avg_purchase_price_nczp(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset_nczp(portfolio=portfolio, asset=asset)
    qs = qs.filter(type_transaction = TypeTransactions.BUY.value)
    qs = qs.aggregate(
            avg_pp=Sum((F('unit_cost') * F('quantity')) + F('other_costs'))/
                Sum(F('quantity'))
        )
    return qs['avg_pp'] if qs['avg_pp'] is not None else Decimal(0)

def get_avg_sale_price(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.filter(type_transaction = TypeTransactions.SELL.value)
    qs = qs.aggregate(
            avg_sp=Sum((F('unit_cost') * F('quantity')) - F('other_costs'))/
                Sum(F('quantity'))
        )
    return qs['avg_sp'] if qs['avg_sp'] is not None else Decimal(0)

def get_avg_sale_price_nczp(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset_nczp(portfolio=portfolio, asset=asset)
    qs = qs.filter(type_transaction = TypeTransactions.SELL.value)
    qs = qs.aggregate(
            avg_sp=Sum((F('unit_cost') * F('quantity')) - F('other_costs'))/
                Sum(F('quantity'))
        )
    return qs['avg_sp'] if qs['avg_sp'] is not None else Decimal(0)

def get_total_cost_portfolio(
    *,
    portfolio: Portfolio
) -> Decimal:

    assets = get_current_assets_portfolio(portfolio=portfolio)
    total = 0
    for asset in assets:
        price = get_avg_purchase_price_nczp(portfolio=portfolio,asset=asset)
        qty = get_qty_asset(portfolio=portfolio,asset=asset)
        total = qty*price
    return total

def get_total_value_portfolio(
    *,
    portfolio: Portfolio
) -> Decimal:
    assets = get_current_assets_portfolio(portfolio=portfolio)
    total = 0
    for asset in assets:
        qty = get_qty_asset(portfolio=portfolio,asset=asset)
        total += qty*asset.current_price
    return total

@transaction.atomic
def reconsolidate_portfolio(
    *,
    portfolio: Portfolio,
    user: User
) -> bool:
    _test_permissions(user=user,
        permission='add_portfolioassetconsolidated',
        object=portfolio)

    Portfolio.objects.filter(pk=portfolio.pk).update(consolidated = False)
    Transaction.objects.filter(
            portfolio__pk=portfolio.pk
        ).update(consolidated = False)
    task_refresh_all_prices()
    return True

@transaction.atomic
def consolidate_portfolio(
    *,
    portfolio: Portfolio,
    user: User
) -> bool:

    _test_permissions(user=user,
        permission='add_portfolioassetconsolidated',
        object=portfolio)

    if portfolio.consolidated:
        return True

    ts = get_transactions(portfolio=portfolio, filters={'consolidated': False})
    ts = ts.values('asset').distinct('asset')
    assets = get_assets(filters={'pk__in':[t['asset'] for t in ts]})

    try:
        all_a = get_all_assets_portfolio(portfolio=portfolio)
        PortfolioAssetConsolidated.objects.filter(portfolio=portfolio).exclude(asset__pk__in=[a.pk for a in all_a]).delete()
    except exceptions.ObjectDoesNotExist:
        pass

    assets_consolidated = get_assets_consolidated(portfolio=portfolio, filters={'asset__pk__in':[a.pk for a in assets]})
    ac_d = {a.asset.ticker: a for a in assets_consolidated}


    for asset in assets:
        if asset.ticker not in ac_d:
            ac = PortfolioAssetConsolidated()
            ac.asset = asset
            ac.portfolio = portfolio
            ac.currency = asset.currency
        else:
            ac = ac_d[asset.ticker]

        qty = get_qty_asset(portfolio=portfolio,asset=asset)
        avg_p_price_nczp = get_avg_purchase_price_nczp(portfolio=portfolio,asset=asset)
        ac.quantity = qty
        #current_price = get_current_price(ticker=asset.ticker)
        ac.avg_p_price = get_avg_purchase_price(portfolio=portfolio,asset=asset)
        ac.avg_p_price_nczp = avg_p_price_nczp
        ac.avg_s_price = get_avg_sale_price(portfolio=portfolio,asset=asset)
        ac.avg_s_price_nczp = get_avg_sale_price_nczp(portfolio=portfolio,asset=asset)
        ac.total_cost = get_total_cost_asset(portfolio=portfolio, asset=asset)
        ac.total_cost_nczp = (qty*avg_p_price_nczp) if qty > 0 else 0
        ac.total_dividend = get_total_dividend_asset(portfolio=portfolio,asset=asset)
        ac.total_dividend_nczp = get_total_dividend_asset_nczp(portfolio=portfolio,asset=asset)
        ac.total_other_cost = get_operation_cost_asset(portfolio=portfolio,asset=asset)
        ac.total_other_cost_nczp = get_operation_cost_asset_nczp(portfolio=portfolio,asset=asset)
        ac.save()

    assets_consolidated = get_assets_consolidated(portfolio=portfolio)
    curr = assets_consolidated.values('currency').distinct('currency')
    currencies = [c['currency'] for c in curr]

    for currency in currencies:
        try:
            pc = get_portfolio_consolidated(portfolio=portfolio, filters={'currency': currency}).get()
        except exceptions.ObjectDoesNotExist:
            pc = PortfolioConsolidated()
            pc.portfolio = portfolio
            pc.currency = currency

        qs = assets_consolidated.filter(currency=currency)
        qs = qs.aggregate(
            sum_tc = Sum('total_cost'),
            sum_tc_nczp = Sum('total_cost_nczp'),
            sum_div = Sum('total_dividend'),
            sum_div_nczp = Sum('total_dividend_nczp'),
            sum_other_cost = Sum('total_other_cost'),
            sum_other_cost_nczp = Sum('total_other_cost_nczp')
        )

        pc.total_cost = qs['sum_tc'] or Decimal(0)
        pc.total_cost_nczp = qs['sum_tc_nczp'] or Decimal(0)
        pc.total_dividend = qs['sum_div'] or Decimal(0)
        pc.total_dividend_nczp = qs['sum_div_nczp'] or Decimal(0)
        pc.total_other_cost = qs['sum_other_cost'] or Decimal(0)
        pc.total_other_cost_nczp = qs['sum_other_cost_nczp'] or Decimal(0)
        pc.save()

    transactions = get_transactions(
        portfolio=portfolio,
        filters={'consolidated': False})
    transactions.update(consolidated=True)

    portfolio.consolidated = True
    portfolio.save()
    return True

def get_results_consolidate(
    *,
    portfolio: Portfolio,
    user: User
) -> dict:
    _test_permissions(user=user,
        permission='add_portfolioassetconsolidated',
        object=portfolio)

    portfolio_c = get_portfolio_consolidated(portfolio=portfolio).first()
    assets_c = get_assets_consolidated(portfolio=portfolio)
    total_portfolio = 0
    for a in assets_c:
        total_portfolio += a.asset.current_price*a.quantity

    results_asset = []

    for a in assets_c:
        total_asset = a.quantity*a.asset.current_price
        result_nczp = total_asset - a.total_cost_nczp
        result = a.total_cost + total_asset
        total_buy_transactions = get_total_buy_transactions(portfolio=portfolio, filters={'asset':a.asset})
        r = {
            'ticker': a.asset.ticker,
            'quantity': a.quantity,
            'current_price': a.asset.current_price,
            'currency': a.asset.currency,
            'last_update': a.asset.last_update,
            'total_cost': a.total_cost,
            'total_cost_nczp': a.total_cost_nczp,
            'total_current': total_asset if a.quantity else 0,
            'portfolio_percentage': (total_asset/total_portfolio)*100 if a.quantity else 0,
            'result_currency_nczp': result_nczp if a.quantity else 0,
            'result_percentage_nczp': (result_nczp/a.total_cost_nczp)*100 if a.quantity else 0,
            'result_currency': result,
            'result_percentage': (result/total_buy_transactions)*100 if total_buy_transactions else 0,
        }
        results_asset += [r]
    return results_asset

def get_ticker_info(
    *,
    ticker: str
) -> dict:
    symbol = None
    url = config('SERVICE_ASSET_INFO')+ticker
    print('URL %s', url)
    response = requests.get(url, timeout=(5, 14))
    if response.status_code == 200:
        try:
            j = json.loads(response.text)
            j = j.get('quotes')
            for quote in j:
                if ticker in quote.get('symbol'):
                    j = quote
                    break
            symbol = re.sub(' +', ' ', j.get('symbol'))
            longname = re.sub(' +', ' ', j.get('longname'))
            shortname = re.sub(' +', ' ', j.get('shortname'))

            return {
                'symbol': symbol,
                'longname': longname,
                'shortname': shortname,
            }
        except (IndexError, AttributeError):
            pass
    return {}



def get_current_price(
    *,
    ticker: str
) -> Decimal:
    symbol = get_ticker_info(ticker=ticker)
    price = 0
    symbol = symbol.get('symbol')

    url = config('SERVICE_PRICES_URL')+str(symbol)
    print('URL %s', url)
    try:
        response = requests.get(url, timeout=(5, 14))
    except requests.exceptions.ConnectionError:
        return 0
    print('response %s %s', ticker, response)
    if response.status_code == 200:
        try:
            j = json.loads(response.text)
            j = j.get('chart')
            j = j.get('result')
            j = j[0]
            j = j.get('meta')
            price = j.get('regularMarketPrice')
            currency = j.get('currency')
        except IndexError:
            raise exceptions.ObjectDoesNotExist
        except AttributeError:
            raise exceptions.ObjectDoesNotExist
    else:
        raise exceptions.ObjectDoesNotExist
    return Decimal(price)

def validate_currency(
    *,
    currency: str
) -> bool:
    if currency in CurrencyChoices.choices:
        return True
    return False
