# Generated by Django 3.2 on 2023-06-07 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store_Monitoring', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='storeId',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]