from django.contrib import admin
from portfolio import models
from django.forms import ModelForm
from django.utils.html import format_html
from django.urls import reverse
from portfolio.selectors import (
    get_portfolios,
    get_fii_transactions_user,
    get_stock_transactions_user
)
from portfolio.services import (
    get_total_value_portfolio,
    create_fii_transaction,
    create_stock_transaction,
)
from portfolio._services import FiiService, StockService, PortfolioService, FiiTransactionService, StockTransactionService
from portfolio.models import Transaction
import logging

class PortfolioAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        save_service = PortfolioService(owner=request.user, **form.cleaned_data)
        if change:
            save_service.update(id=obj.pk)
        else:
            save_service.save()

    def get_queryset(self, request):
        return PortfolioService(owner=request.user).get_list()

    def get_total(obj):
        return "%2.2f" % (get_total_value_portfolio(portfolio=obj))

    get_total.short_description = 'Total Value'

    def show_view_link(obj):
        return format_html(
            "<a href='{0}'>Visualizar</a>", reverse('view_portfolio', args=[obj.pk])
        )

    show_view_link.short_description = ''

    def show_consolidate_link(obj):
        return format_html(
            "<a href='{0}'>Re-Consolidar</a>",
            reverse('reconsolidate_portfolio', args=[obj.pk]),
        )

    show_consolidate_link.short_description = ''

    list_display = (
        'name',
        'desc_1',
        #get_total,
        'created_at',
        show_consolidate_link,
        show_view_link,
    )
    exclude = [
        'owner',
        'consolidated',
    ]
    readonly_fields = [
        'owner',
    ]


class AssetAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list_with_upload.html'
    search_fields = (
        'ticker',
        'name',
    )
    exclude = [
        'current_price',
    ]
    list_filter = ['type_investment']

    def get_current_price(obj):
        if obj.current_price > 0:
            return "%s %2.2f" % (obj.currency, obj.current_price)
        else:
            return format_html("<a href='.'>Atualizar</a>")

    get_current_price.short_description = 'Current Price'

    list_display = ('ticker', 'name', get_current_price, 'last_update')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_file_url'] = reverse('asset_upload_file')
        return super(AssetAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    def get_search_results(self, request, queryset, search_term):
        result = {
            reverse('admin:portfolio_fiitransaction_add'): FiiService,
            reverse('admin:portfolio_stocktransaction_add'): StockService,
        }

        url = request.META.get('HTTP_REFERER')
        url = url[url.index('/admin/') :] if url else None

        if url in result:
            queryset = result[url]().get_list()
        else:
            queryset = queryset
        queryset, use_distinct = super(AssetAdmin, self).get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct
    
    def get_asset_service(self, type_investment):
        services = {'FII': FiiService, 'STOCK': StockService}
        return services[type_investment]

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        save_service = self.get_asset_service(obj.type_investment)
        save_service = save_service(**form.cleaned_data)
        if change:
            save_service.update(id=obj.pk)
        else:
            save_service.save()
    
    def delete_model(self, request, obj):
        delete_service = self.get_asset_service(obj.type_investment)
        delete_service().delete(obj.pk)
    
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)


class TransactionForm(ModelForm):
    # asset = CharField(validators=[])
    # type_investment = CharField(widget=HiddenInput)

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
            'desc_2',
        )

    """def clean_asset(self):
        asset = self.cleaned_data.get('asset')
        type_investment = self.cleaned_data.get('type_investment')
        asset = create_asset(ticker=asset)
        return asset

    def get_initial_for_field(self, field, field_name):
        if field_name == 'asset':
            if hasattr(self.instance, 'asset') and isinstance(self.instance.asset, Asset):
                return self.instance.asset.ticker
        return super().get_initial_for_field(field, field_name)"""


class TransactionAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list_with_upload.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_file_url'] = reverse('transactions_upload_file')
        return super(TransactionAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    # To return only portfolio's current user on portfolio field at forms
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'portfolio':
            kwargs['queryset'] = get_portfolios(fetched_by=request.user)
        return super(TransactionAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_asset(obj):
        return obj.asset.ticker

    get_asset.short_description = 'Asset'

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

    autocomplete_fields = ['asset']
    list_display = (
        'type_transaction',
        get_asset,
        'desc_1',
        get_transaction_date,
        get_unit_cost,
        get_quantity,
        get_total,
    )
    search_fields = (
        'asset__name',
        'asset__ticker',
        'transaction_date',
        'stockbroker',
        'desc_1',
        'desc_2',
    )
    list_filter = ['stockbroker', 'type_transaction']


class StockTransactionAdmin(TransactionAdmin):
    form = TransactionForm

    def get_service(self, request):
        service = StockTransactionService(owner=request.user)
        return service

    def get_queryset(self, request):
        service = self.get_service(request)
        return service.get_list()

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        save_service = StockTransactionService(owner=request.user, **form.cleaned_data)
        if change:
            save_service.update(id=obj.pk)
        else:
            save_service.save()


class FiiTransactionAdmin(TransactionAdmin):
    form = TransactionForm

    def get_service(self, request):
        service = FiiTransactionService(owner=request.user)
        return service

    def get_queryset(self, request):
        service = self.get_service(request)
        return service.get_list()

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        save_service = FiiTransactionService(owner=request.user, **form.cleaned_data)
        if change:
            save_service.update(id=obj.pk)
        else:
            save_service.save()


admin.site.register(models.AssetType)
admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Portfolio, PortfolioAdmin)
admin.site.register(models.StockTransaction, StockTransactionAdmin)
admin.site.register(models.FiiTransaction, FiiTransactionAdmin)
