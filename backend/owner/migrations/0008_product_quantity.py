# Generated by Django 5.1.6 on 2025-02-18 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0007_category_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
