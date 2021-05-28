from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from .models import Portfolio, PortfolioAssetConsolidated, Asset
from portfolio.services import (
    consolidate_portfolio,
    reconsolidate_portfolio as reconsolidate,
    create_asset,
    create_transaction,
    get_current_price,
    validate_currency,
    get_results_consolidate
    )
from portfolio.selectors import (
    get_portfolios,
    get_assets,
    get_portfolio_consolidated,
    get_assets_consolidated,
    get_current_assets_portfolio
    )
from portfolio._services import asset as asset_service
from .forms import AssetUploadFileForm, TransactionUploadFileForm
import decimal
import csv, io, datetime, logging
import pandas as pd

def view_portfolio(request, portfolio_id):
    portfolio = get_portfolios(
        fetched_by=request.user, filters={'pk':portfolio_id}).get()

    consolidate_portfolio(portfolio=portfolio, user=request.user)

    portfolio_c = get_portfolio_consolidated(portfolio=portfolio).first()
    assets_c = get_assets_consolidated(portfolio=portfolio, filters={'quantity__gt':0})
    results = {r['ticker']: r for r in get_results_consolidate(portfolio=portfolio, user=request.user)}

    return render(request, 'portfolio/detail.html',
        {'asset_list': assets_c, 'results': results, 'portfolio': portfolio_c})

def reconsolidate_portfolio(request, portfolio_id):
    portfolio = get_portfolios(
        fetched_by=request.user, filters={'pk':portfolio_id}).get()
    reconsolidate(portfolio=portfolio, user=request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def asset_upload_file(request):
    if request.method == 'POST':
        form = AssetUploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = request.FILES['myfile']
            data_csv = pd.read_csv(
                myfile, 
                delimiter=';',
                usecols=['ticker',
                    'name',
                    'type_investment',
                    'desc_3'])
            row_iter = data_csv.iterrows()
            services = {
                'FII': asset_service.FiiService,
                'STOCK': asset_service.StockService
            }
            for index, row in row_iter:
                service = services[row['type_investment']]
                service = service(ticker=row['ticker'],
                    name=row['name'][0:60],
                    type_investment=row['type_investment'],
                    desc_3=row['desc_3'][0:100])
                service.save()

            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            return render(request, 'portfolio/upload_files.html', {
                'uploaded_file_url': uploaded_file_url
            })
    else:
        form = AssetUploadFileForm()
    return render(request, 'portfolio/upload_files.html', {'form': form})

def transactions_upload_file(request):

    def convert_str_dec(text):
        dec = 0
        text = text.lstrip()
        text = text if len(text) > 0 else '0'
        try:
            text = text.replace(',','.')
            text = text.replace('R$','')
            text = text.replace('$','')
            text = text.replace('€','')
            dec = decimal.Decimal(text)
        except decimal.InvalidOperation:
            raise decimal.InvalidOperation
        return dec

    if request.method == 'POST':
        form = TransactionUploadFileForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage()
            myfile = request.FILES['myfile']
            portfolio = get_portfolios(fetched_by=request.user).get(
                pk=request.POST['portfolio'])

            paramFile = io.TextIOWrapper(myfile)
            lines = csv.DictReader(paramFile, delimiter=";")
            list_of_dict = list(lines)
            #print(list_of_dict)
            with transaction.atomic():
                for row in list_of_dict:
                    asset = get_assets(filters={'ticker': row['ticker']})[0]
                    if validate_currency(currency=row.get('currency', 'R$').lstrip()):
                        currency = row.get('currency', 'R$').lstrip()
                    else:
                        raise Exception('Invalid Currency')

                    t = create_transaction(
                        portfolio = portfolio,
                        type_transaction = row['transaction'].lstrip(),
                        transaction_date = datetime.datetime.strptime(row['date']+' 00:00', '%d/%m/%Y %H:%M'),
                        asset = asset,
                        quantity = convert_str_dec(row['qty']),
                        unit_cost = convert_str_dec(row['avg_price']),
                        currency = currency,
                        other_costs = convert_str_dec(row.get('other_costs', '0')),
                        desc_1=row.get('desc_1', '')[0:20].lstrip(),
                        desc_2=row.get('desc_2', '')[0:100].lstrip())

            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            return render(request, 'portfolio/upload_files.html', {
                'uploaded_file_url': uploaded_file_url
            })
    else:
        form = TransactionUploadFileForm(request.user)
    return render(request, 'portfolio/upload_files.html', {'form': form})
