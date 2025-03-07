# Generated by Django 5.1.6 on 2025-02-20 05:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('owner', '0009_remove_product_quantity'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('role', models.CharField(choices=[('Owner', 'Owner'), ('Staff', 'Staff')], max_length=10)),
                ('shop_type', models.CharField(blank=True, choices=[('restaurant', 'Restaurant'), ('liquor_store', 'Liquor Store')], max_length=20, null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='customuser_set', to='auth.group')),
                ('restaurant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='owner.restaurant')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='customuser_permissions_set', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
