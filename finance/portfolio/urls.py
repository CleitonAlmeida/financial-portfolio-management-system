from django.urls import path
from . import views

urlpatterns = [
        path('<int:portfolio_id>/', views.view_portfolio,
            name='view_portfolio'),
        path('<int:portfolio_id>/reconsolidate_portfolio', views.reconsolidate_portfolio,
            name='reconsolidate_portfolio'),
        path('asset/upload_file', views.asset_upload_file,
            name='asset_upload_file'),
        path('transactions/upload_file', views.transactions_upload_file,
            name='transactions_upload_file')
]
