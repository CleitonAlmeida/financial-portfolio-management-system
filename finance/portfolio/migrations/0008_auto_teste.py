from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0007_auto_teste'),
    ]

    operations = [
        migrations.CreateModel(
            name='fiitransaction',
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
