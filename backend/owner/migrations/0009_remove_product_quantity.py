# Generated by Django 5.1.6 on 2025-02-18 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0008_product_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
    ]
