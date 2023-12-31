# Generated by Django 3.2 on 2023-06-10 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store_Monitoring', '0002_alter_store_storeid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reportId', models.CharField(max_length=20, unique=True)),
                ('status', models.CharField(choices=[('R', 'Running'), ('C', 'Completed')], max_length=1)),
                ('data', models.TextField()),
            ],
        ),
    ]
