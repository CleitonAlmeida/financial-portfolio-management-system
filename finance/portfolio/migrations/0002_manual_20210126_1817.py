from django.db import migrations

def create_assettypes(apps, schema_editor):
    asset_types = ['STOCK', 'FII']
    AssetType = apps.get_model('portfolio', 'AssetType')
    for type in asset_types:
        at = AssetType(name=type)
        at.save()

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_assettypes),
    ]
