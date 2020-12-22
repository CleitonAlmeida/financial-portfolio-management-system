from django.urls import path
from . import views

urlpatterns = [
        path('<int:portfolio_id>/', views.view_portfolio, name='view_portfolio')
]
