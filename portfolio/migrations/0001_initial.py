# Generated by Django 3.1.3 on 2021-01-26 20:54

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('ticker', models.CharField(max_length=7, unique=True)),
                ('currency', models.CharField(choices=[('R$', 'Reais'), ('$', 'Dolar'), ('€', 'Euro')], default='R$', max_length=5)),
                ('desc_1', models.CharField(blank=True, max_length=20, null=True)),
                ('desc_2', models.CharField(blank=True, max_length=50, null=True)),
                ('desc_3', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True)),
                ('desc_1', models.CharField(blank=True, max_length=20, null=True)),
                ('consolidated', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_transaction', models.CharField(choices=[('C', 'Compra'), ('V', 'Venda'), ('Div', 'Dividendo'), ('Jcp', 'Juros s/ Capital')], max_length=3)),
                ('transaction_date', models.DateTimeField()),
                ('quantity', models.DecimalField(decimal_places=5, max_digits=12)),
                ('unit_cost', models.DecimalField(decimal_places=5, max_digits=12)),
                ('currency', models.CharField(choices=[('R$', 'Reais'), ('$', 'Dolar'), ('€', 'Euro')], default='R$', max_length=5)),
                ('other_costs', models.DecimalField(blank=True, decimal_places=5, default=0, max_digits=8)),
                ('desc_1', models.CharField(blank=True, max_length=20, null=True)),
                ('desc_2', models.CharField(blank=True, max_length=100, null=True)),
                ('stockbroker', models.CharField(blank=True, choices=[('CL', 'Clear'), ('XP', 'XP Investimentos'), ('RI', 'Rico'), ('AV', 'Avenue'), ('TD', 'TD Ameritrade')], max_length=2, null=True)),
                ('consolidated', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='portfolio.asset')),
                ('portfolio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio')),
                ('type_investment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='portfolio.assettype')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioConsolidated',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(choices=[('R$', 'Reais'), ('$', 'Dolar'), ('€', 'Euro')], default='R$', max_length=5)),
                ('total_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_cost_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_dividend', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_dividend_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_other_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_other_cost_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioAssetConsolidated',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(choices=[('R$', 'Reais'), ('$', 'Dolar'), ('€', 'Euro')], default='R$', max_length=5)),
                ('quantity', models.DecimalField(decimal_places=5, default=Decimal('0'), max_digits=12)),
                ('avg_p_price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('avg_p_price_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('avg_s_price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('avg_s_price_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_cost_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_dividend', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_dividend_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_other_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('total_other_cost_nczp', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='portfolio.asset')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio')),
            ],
        ),
        migrations.AddField(
            model_name='asset',
            name='type_investment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.assettype'),
        ),
        migrations.CreateModel(
            name='FiiTransaction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('portfolio.transaction',),
        ),
        migrations.CreateModel(
            name='StockTransaction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('portfolio.transaction',),
        ),
    ]