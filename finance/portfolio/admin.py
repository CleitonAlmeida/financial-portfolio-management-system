from django.contrib import admin

# Register your models here.
from .models import Portfolio, Asset, AssetType, StockTransaction, FiiTransaction
from django.forms import ModelChoiceField, CharField, ModelForm, BaseModelForm, TextInput, Textarea
from django.db.models import Sum, F
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import AdminSite
from portfolio.selectors import (
    get_portfolios,
    get_fii_transactions_user,
    get_stock_transactions_user
)
from portfolio.services import (
    get_total_cost_portfolio,
    create_portfolio,
    create_fii_transaction,
    create_stock_transaction,
    get_or_create_asset
)
from portfolio.models import Transaction

class PortfolioAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        if change:
            return super().save_model(request, obj, form, change)
        create_portfolio(owner=request.user,**form.cleaned_data)

    def get_queryset(self, request):
        return get_portfolios(fetched_by=request.user)

    def get_total(obj):
        return "%2.2f" % (get_total_cost_portfolio(portfolio=obj))
    get_total.short_description = 'Total Cost'

    def show_view_link(obj):
        return format_html("<a href='{0}'>Visualizar</a>", reverse('view_portfolio', args=[obj.pk]))
    show_view_link.short_description = 'Visualizar'

    list_display = ('name',
        'desc_1',
        get_total,
        'created_at',
        show_view_link)
    exclude = ['owner','consolidated',]
    readonly_fields = [
        'owner',
    ]

class TransactionForm(ModelForm):
    asset = CharField(validators=[])

    class Meta:
        model = Transaction
        fields = (
            'portfolio',
            'type_transaction',
            'transaction_date',
            #'type_investment',
            'asset',
            'quantity',
            'unit_cost',
            'currency',
            'other_costs',
            'stockbroker',
            'desc_1',
            'desc_2'
        )
        #hidden = ['type_investment']

    def clean_asset(self):
        asset = self.cleaned_data.get('asset')
        type_investment = self.cleaned_data.get('type_investment')
        asset = get_or_create_asset(ticker=asset, type_investment=type_investment)
        return asset

    def get_initial_for_field(self, field, field_name):
        if field_name == 'asset':
            if hasattr(self.instance, 'asset') and isinstance(self.instance.asset, Asset):
                return self.instance.asset.ticker
        return super().get_initial_for_field(field, field_name)

class TransactionAdmin(admin.ModelAdmin):

    # To return only portfolio's current user on portfolio field at forms
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'portfolio':
            kwargs['queryset'] = get_portfolios(fetched_by=request.user)
        return super(TransactionAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def get_unit_cost(obj):
        return "%s %2.2f" % (obj.currency, obj.unit_cost)
    get_unit_cost.short_description = 'Unit Cost'

    def get_quantity(obj):
        return "%2.2f" % obj.quantity
    get_quantity.short_description = 'Quantity'

    def get_total(obj):
        return "%s %2.2f" % (obj.currency, 0)
    get_total.short_description = 'Total'

    def get_transaction_date(obj):
        return obj.transaction_date.strftime("%d/%b/%Y")
    get_transaction_date.short_description = 'Date'

    list_display = ('portfolio',
        'asset',
        'desc_1',
        get_transaction_date,
        get_unit_cost,
        get_quantity,
        get_total,
        )
    search_fields = (
        'asset',
        'transaction_date',
        'stockbroker',
        'desc_1',
        'desc_2')
    list_filter = ['stockbroker']


class StockTransactionAdmin(TransactionAdmin):
    form = TransactionForm

    def get_queryset(self, request):
        return get_stock_transactions_user(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        if change:
            return super().save_model(request, obj, form, change)
        form.cleaned_data.pop('type_investment')
        create_stock_transaction(user=request.user,**form.cleaned_data)

class FiiTransactionAdmin(TransactionAdmin):
    form = TransactionForm

    def get_queryset(self, request):
        return get_fii_transactions_user(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        if change:
            return super().save_model(request, obj, form, change)
        if 'type_investment' in form.cleaned_data:
            form.cleaned_data.pop('type_investment')
        create_fii_transaction(user=request.user,**form.cleaned_data)

admin.site.register(AssetType)
admin.site.register(Asset)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(StockTransaction, StockTransactionAdmin)
admin.site.register(FiiTransaction, FiiTransactionAdmin)
