# Generated by Django 3.1.3 on 2021-02-26 03:59

from django.db import migrations, models

def update_acronym(apps, schema_editor):
    Transaction = apps.get_model('portfolio', 'Transaction')
    Transaction.objects.filter(type_transaction='C').update(type_transaction='B')
    Transaction.objects.filter(type_transaction='V').update(type_transaction='S')
    Transaction.objects.filter(type_transaction='Jcp').update(type_transaction='Div')

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_auto_20210226_0237'),
    ]

    operations = [
        migrations.RunPython(update_acronym),
        migrations.AlterField(
            model_name='transaction',
            name='type_transaction',
            field=models.CharField(choices=[('B', 'Buy'), ('S', 'Sell'), ('Div', 'Dividend')], max_length=3),
        ),
    ]
