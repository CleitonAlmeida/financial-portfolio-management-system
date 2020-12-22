from django.shortcuts import render
from django.http import Http404
from .models import Portfolio, PortfolioConsolidated
from portfolio.services import consolidate_portfolio

def view_portfolio(request, portfolio_id):
    try:
        consolidate_portfolio(id=portfolio_id, user=request.user)
    except:
        raise Http404("Portfolio does not exist")
    portfolio_c = PortfolioConsolidated()
    portfolio_c = PortfolioConsolidated.objects.filter(portfolio__pk=portfolio_id)
    return render(request, 'portfolio/detail.html', {'asset_list': portfolio_c})
