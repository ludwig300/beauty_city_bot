from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField


class User(models.Model):
    full_name = models.CharField(
        'ФИО владельца',
        max_length=200,
        db_index=True
    )
    phoneNumber = PhoneNumberField(
        unique=True,
        null=False,
        blank=False
    )

    def __str__(self):
        return self.full_name

class Salon(models.Model):
    salon_name = models.CharField(
        'Наименование салона', max_length=200, db_index=True,
    )
    address = models.TextField(
        'Адрес Салона', blank=True, null=True)

    def __str__(self):
        return self.salon_name


class Service(models.Model):
    service_name = models.CharField(
        'Наименование услуги', max_length=200, db_index=True,
    )
    price = models.IntegerField('Цена услуги', db_index=True)

    def __str__(self):
        return self.service_name


class Specialist(models.Model):
    full_name = models.CharField(
        'ФИО Специалиста', max_length=200, db_index=True,
    )
    salon = models.ForeignKey(
        Salon, on_delete=models.CASCADE,
        verbose_name='Салон'
    )
    services = models.ManyToManyField(
        Service, related_name="services",
        verbose_name='Услуги специалиста',
        blank=True
    )

    def __str__(self):
        return self.full_name


class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='schedules_user',
                             verbose_name='Имя клиента')
    date_time = models.DateTimeField(
        'дата и время посещения',
        db_index=True
    )
    salon = models.ForeignKey(
        Salon, on_delete=models.CASCADE,
        verbose_name='Салон'
    )
    specialist = ChainedForeignKey(
        Specialist,
        chained_field="salon",
        chained_model_field="salon",
        show_all=False,
        sort=True,
        on_delete=models.CASCADE,
        verbose_name='Специалист'
    )

    service = ChainedManyToManyField(
        Service,
        horizontal=True,
        chained_field="specialist",
        chained_model_field="services",
        verbose_name='Услуга',

    )

    def __unicode__(self):
        return self.user

