# Generated by Django 5.1.6 on 2025-02-20 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owner', '0011_alter_restaurant_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('Owner', 'Owner'), ('Staff', 'Staff')], default='Owner', max_length=10),
        ),
    ]
