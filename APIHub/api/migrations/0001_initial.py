# Generated by Django 5.1.5 on 2025-01-26 23:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.TextField(blank=True, null=True)),
                ('short_name', models.TextField(blank=True, null=True)),
                ('short_name_english', models.TextField(blank=True, null=True)),
                ('judicial_address', models.TextField(blank=True, null=True)),
                ('email', models.TextField(blank=True, null=True)),
                ('leader', models.TextField(blank=True, null=True)),
                ('registration_date', models.DateTimeField(blank=True, null=True)),
                ('okved', models.CharField(blank=True, max_length=10, null=True)),
                ('index_due_diligence', models.IntegerField(blank=True, null=True)),
                ('index_due_diligence_word', models.TextField(blank=True, null=True)),
                ('inn', models.CharField(blank=True, max_length=12, null=True, unique=True)),
                ('kpp', models.CharField(blank=True, max_length=9, null=True)),
                ('ogrn', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('okpo', models.CharField(blank=True, max_length=12, null=True)),
                ('okfs', models.TextField(blank=True, null=True)),
                ('okopf', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('role', models.CharField(choices=[('admin', 'Administrator'), ('customer', 'Customer'), ('supplier', 'Supplier')], default='customer', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_permissions', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('okpd2', models.CharField(max_length=255, verbose_name='Сфера деятельности по ОКПД2')),
                ('description', models.TextField(verbose_name='Описание заказа')),
                ('contract_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма контракта')),
                ('delivery_region', models.CharField(max_length=255, verbose_name='Регион поставки')),
                ('law_type', models.CharField(choices=[('44_FZ', '44-ФЗ'), ('223_FZ', '223-ФЗ')], default='44_FZ', max_length=6, verbose_name='Закон, по которому организуется заказ')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Заказчик')),
            ],
        ),
    ]
