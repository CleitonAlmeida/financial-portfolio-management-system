from django.contrib.auth.models import User
from django.core import exceptions
from django.utils import timezone
from django.db.models import (
    Sum,
    F,
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
    PortfolioConsolidated
)
from portfolio.selectors import (
    get_transactions_asset,
    get_transactions
)
from typing import (
    Optional,
    Union,
    NewType,
    Iterable
)
from decimal import Decimal
import datetime
from enum import Enum
import requests, json, re

class TypeTransaction(Enum):
    Buy = 'C'
    Sell = 'V'
    Dividend = 'Div'
    JCP = 'JCP'
TypeTransactions = NewType('TypeTransactions', TypeTransaction)

class CurrencyChoice(Enum):
    Reais = 'R$'
    Dolar = '$'
    Euro = '€'
CurrencyChoices = NewType('CurrencyChoices', CurrencyChoice)

class StockBrokerChoice(Enum):
    Clear = 'CL'
    XP = 'XP'
    Rico = 'RI'
    Avenue = 'AV'
    TDAmeritrade = 'TD'
StockBrokerChoices = NewType('StockBrokerChoices', StockBrokerChoice)

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
                print("has_permission object %s %s", permission, has_permission)
                raise exceptions.PermissionDenied
        else:
            raise exceptions.PermissionDenied
    else:
        app_label = 'portfolio'

    has_permission = user.has_perm(app_label+'.'+permission)
    print("has_permission object %s %s", permission, has_permission)
    if not has_permission:
        raise exceptions.PermissionDenied

def create_portfolio(
    *,
    owner: User,
    name: str,
    desc_1: str = None,
) -> Portfolio:
    _test_permissions(user=owner,permission='add_portfolio')
    portfolio = Portfolio.objects.create(
        owner=owner,
        name=name,
        desc_1=desc_1,
    )

    return portfolio

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

def get_or_create_asset(
    *,
    ticker: str,
    type_investment: Optional[AssetType] = None,
    name: str = None,
    desc_1: str = None,
    desc_2: str = None,
    desc_3: str = None,
) -> Asset:
    filter = {'ticker': ticker}
    if type_investment is not None:
        filter['type_investment'] = type_investment
    try:
        asset = Asset.objects.get(**filter)
    except exceptions.ObjectDoesNotExist:
        if name is None:
            asset_info = get_ticker_info(ticker=ticker)
            print('Passandnooo %s %s', type(asset_info), asset_info)
            if type(asset_info) == dict:
                name = asset_info.get('longname')
                desc_1 = asset_info.get('shortname')
                desc_2 = asset_info.get('symbol')
        asset = Asset.objects.create(
            ticker=ticker,
            type_investment=type_investment,
            name=name,
            desc_1=desc_1,
            desc_2=desc_2,
            desc_3=desc_3,
        )
    return asset

def create_transaction(
    *,
    portfolio: Portfolio,
    type_transaction: Optional[TypeTransactions],
    type_investment: Union[str,AssetType] = None,
    transaction_date: datetime = timezone.now(),
    asset: Union[str, Asset],
    quantity: Union[int,float,Decimal],
    unit_cost: Union[int,float,Decimal],
    currency: Optional[CurrencyChoices]=CurrencyChoice.Reais.value,
    other_costs: Union[int,float,Decimal] = Decimal('0.0'),
    desc_1:str = None,
    desc_2:str = None,
    stockbroker: Optional[StockBrokerChoices] = StockBrokerChoice.Rico.value,
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
        asset = get_or_create_asset(**params)
    transaction = Transaction.objects.create(
        portfolio=portfolio,
        type_transaction=type_transaction,
        transaction_date=transaction_date,
        asset=asset,
        type_investment=asset.type_investment,
        quantity=quantity,
        unit_cost=unit_cost,
        currency=currency,
        other_costs=other_costs,
        desc_1=desc_1,
        desc_2=desc_2,
        stockbroker=stockbroker,
    )
    return transaction

def create_fii_transaction(
    *,
    user: User,
    portfolio: Portfolio,
    type_transaction: Optional[TypeTransactions],
    transaction_date: datetime = timezone.now(),
    asset: Union[str, Asset],
    quantity: Union[int,float,Decimal],
    unit_cost: Union[int,float,Decimal],
    currency: Optional[CurrencyChoices]=CurrencyChoice.Reais.value,
    other_costs: Union[int,float,Decimal] = Decimal('0.0'),
    desc_1:str = None,
    desc_2:str = None,
    stockbroker: Optional[StockBrokerChoices] = StockBrokerChoice.Rico.value,
) -> Transaction:
    _test_permissions(user=user,permission='add_fiitransaction')
    return create_transaction(
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
    portfolio: Portfolio,
    type_transaction: Optional[TypeTransactions],
    transaction_date: datetime = timezone.now(),
    asset: Union[str, Asset],
    quantity: Union[int,float,Decimal],
    unit_cost: Union[int,float,Decimal],
    currency: Optional[CurrencyChoices]=CurrencyChoice.Reais.value,
    other_costs: Union[int,float,Decimal] = Decimal('0.0'),
    desc_1:str = None,
    desc_2:str = None,
    stockbroker: Optional[StockBrokerChoices] = StockBrokerChoice.Rico.value,
) -> Transaction:
    _test_permissions(user=user,permission='add_stocktransaction')
    return create_transaction(
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
            When(type_transaction=TypeTransaction.Buy.value, then=F('quantity')),
            When(type_transaction=TypeTransaction.Sell.value, then=F('quantity')*-1),
        )
    )
    qs = qs.aggregate(Sum(F('qty')))
    return qs['qty__sum'] if qs['qty__sum'] is not None else Decimal(0)

def get_total_value_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.annotate(
        qty=Case(
            When(type_transaction=TypeTransaction.Buy.value, then=(
                (F('unit_cost') * F('quantity')) + F('other_costs')
            )),
            When(type_transaction=TypeTransaction.Sell.value, then=(
                ((F('unit_cost') * F('quantity')) + F('other_costs'))*-1
            )),
        )
    )
    qs = qs.aggregate(Sum(F('qty')))
    return qs['qty__sum'] if qs['qty__sum'] is not None else Decimal(0)

def get_operation_cost_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.aggregate(total_cost=Sum('other_costs'))
    return qs['total_cost'] if qs['total_cost'] is not None else Decimal(0)

def get_avg_price_asset(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qty = get_qty_asset(portfolio=portfolio, asset=asset)
    if qty > 0:
        total = get_total_value_asset(portfolio=portfolio, asset=asset)
        return total/qty
    else:
        return 0

def get_avg_purchase_price(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    qs = get_transactions_asset(portfolio=portfolio, asset=asset)
    qs = qs.filter(type_transaction = TypeTransaction.Buy.value)
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
    qs = qs.filter(type_transaction = TypeTransaction.Sell.value)
    qs = qs.aggregate(
            avg_sp=Sum((F('unit_cost') * F('quantity')) + F('other_costs'))/
                Sum(F('quantity'))
        )
    return qs['avg_sp'] if qs['avg_sp'] is not None else Decimal(0)

def get_total_cost_portfolio(
    *,
    portfolio: Portfolio
) -> Decimal:
    qs = get_transactions(portfolio=portfolio)
    qs = qs.annotate(
        qty=Case(
            When(type_transaction=TypeTransaction.Buy.value, then=(
                (F('unit_cost') * F('quantity')) + F('other_costs')
            )),
            When(type_transaction=TypeTransaction.Sell.value, then=(
                ((F('unit_cost') * F('quantity')) + F('other_costs'))*-1
            )),
        )
    )
    qs = qs.aggregate(Sum(F('qty')))
    return qs['qty__sum'] if qs['qty__sum'] is not None else Decimal(0)


def get_percentage_portfolio(
    *,
    portfolio: Portfolio,
    asset: Asset
) -> Decimal:
    total_portfolio = get_total_cost_portfolio(portfolio=portfolio)
    total_asset = get_total_value_asset(portfolio=portfolio, asset=asset)
    return round((total_asset/total_portfolio)*100, 2)


def consolidate_portfolio(
    *,
    id: int,
    user: User
) -> bool:
    try:
        portfolio = Portfolio.objects.get(pk=id)
    except exceptions.ObjectDoesNotExist:
        return False

    _test_permissions(user=user,
        permission='add_portfolioconsolidated',
        object=portfolio)

    if portfolio.consolidated:
        return True

    try:
        PortfolioConsolidated.objects.filter(portfolio__pk=id).delete()
    except exceptions.ObjectDoesNotExist:
        pass

    qs = get_transactions(portfolio=portfolio)
    qs = qs.distinct('asset').all()

    for q in qs:
        print(' qqqq %s', q.asset.ticker)
        asset = Asset.objects.get(ticker=q.asset.ticker)
        qty = get_qty_asset(portfolio=portfolio,asset=asset)
        current_price = get_current_price(ticker=asset.ticker)
        line = {
            'portfolio': portfolio,
            'asset': asset,
            'quantity': qty,
            'avg_price': get_avg_price_asset(portfolio=portfolio,asset=asset),
            'current_price': current_price,
            'total': qty*current_price,
            'result_currency': 0.0,
            'result_percentage': 0.0,
            'total_dividend': 0.0
        }
        pc = PortfolioConsolidated(**line)
        pc.save()
    portfolio.consolidated = True
    portfolio.save()
    return True


def get_ticker_info(
    *,
    ticker: str
) -> dict:
    symbol = None
    url = 'https://query2.finance.yahoo.com/v1/finance/search?q={0}'.format(ticker)
    response = requests.get(url)
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
        except IndexError:
            raise exceptions.ObjectDoesNotExist
        except AttributeError:
            raise exceptions.ObjectDoesNotExist
    else:
        raise exceptions.ObjectDoesNotExist

    return {
        'symbol': symbol,
        'longname': longname,
        'shortname': shortname,
    }

def get_current_price(
    *,
    ticker: str
) -> Decimal:
    symbol = get_ticker_info(ticker=ticker)
    price = 0
    symbol = symbol.get('symbol')

    url = 'https://query1.finance.yahoo.com/v8/finance/chart/{0}'.format(symbol)
    response = requests.get(url)
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
