# Generated by Django 4.1.4 on 2022-12-07 16:27

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import smart_selects.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Salon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salon_name', models.CharField(db_index=True, max_length=200, verbose_name='Наименование салона')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Адрес Салона')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(db_index=True, max_length=200, verbose_name='Наименование услуги')),
                ('price', models.IntegerField(db_index=True, verbose_name='Цена услуги')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(db_index=True, max_length=200, verbose_name='ФИО владельца')),
                ('phoneNumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Specialist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(db_index=True, max_length=200, verbose_name='ФИО Специалиста')),
                ('salon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.salon', verbose_name='Салон')),
                ('services', models.ManyToManyField(blank=True, related_name='services', to='services.service', verbose_name='Услуги специалиста')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(db_index=True, verbose_name='дата и время посещения')),
                ('salon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.salon', verbose_name='Салон')),
                ('service', smart_selects.db_fields.ChainedManyToManyField(chained_field='specialist', chained_model_field='services', horizontal=True, to='services.service', verbose_name='Услуга')),
                ('specialist', smart_selects.db_fields.ChainedForeignKey(chained_field='salon', chained_model_field='salon', on_delete=django.db.models.deletion.CASCADE, to='services.specialist', verbose_name='Специалист')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules_user', to='services.user', verbose_name='Имя клиента')),
            ],
        ),
    ]
