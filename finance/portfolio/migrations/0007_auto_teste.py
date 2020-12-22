from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_auto_20201115_0456'),
    ]

    operations = [
        migrations.CreateModel(
            name='stocktransaction',
            fields=[
            ],
            options={
                'db_table': 'transaction',
                'managed': False,
                'proxy': True
            },
            bases=('portfolio.transaction',),
        ),
    ]
