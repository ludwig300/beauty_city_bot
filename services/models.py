from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from smart_selects.db_fields import ChainedForeignKey


class User(models.Model):
    order_datetime = models.DateTimeField(
        'Дата и время регистрации на посещение',
        blank=False,
    )
    user_name = models.CharField(
        'ФИО Пользователя',
        max_length=200,
        db_index=True
    )
    phoneNumber = PhoneNumberField(
        unique=True,
        null=False,
        blank=False
    )
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)

    def __str__(self):
        return self.user_name


class Salon(models.Model):
    salon_name = models.CharField(
        'Наименование салона', max_length=200, db_index=True,
    )
    address = models.TextField(
        'Адрес Салона', blank=True, null=True)

    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)

    def __str__(self):
        return self.salon_name


class Service(models.Model):
    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон',
        related_name="salon_service",
        blank=True,
        on_delete=models.CASCADE,
    )

    service_name = models.CharField(
        'Наименование услуги', max_length=200, db_index=True,
    )
    price = models.IntegerField('Цена услуги', db_index=True)

    def __str__(self):
        return f'Салон: {self.salon}. Услуга:{self.service_name}. Цена: {self.price}.'


class Specialist(models.Model):
    full_name = models.CharField(
        'ФИО Специалиста',
        max_length=200,
        db_index=True,
    )
    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон, в котором работает Мастер',
        related_name="salon",
        blank=True,
        on_delete=models.CASCADE,
    )
    services = models.ManyToManyField(
        Service, related_name="services",
        verbose_name='Услуги специалиста',
        blank=True
    )

    def __str__(self):
        return self.full_name


class Schedule(models.Model):
    class Meta:
        unique_together = ('specialist', 'date', 'timeslot')

    TIMESLOT_LIST = (
        (0, '09:00 – 10:00'),
        (1, '10:00 – 11:00'),
        (2, '11:00 – 12:00'),
        (3, '12:00 – 13:00'),
        (4, '13:00 – 14:00'),
        (5, '15:00 – 16:00'),
        (6, '16:00 – 17:00'),
        (7, '17:00 – 18:00'),
        (8, '18:00 – 19:00'),
    )

    date = models.DateField('Дата посещения', help_text="YYYY-MM-DD")
    timeslot = models.IntegerField(choices=TIMESLOT_LIST, null=True)

    user = models.ForeignKey(
        User,
        verbose_name='Имя клиента',
        on_delete=models.CASCADE,
        related_name='schedules_user',
        blank=False,
    )

    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон',
        on_delete=models.CASCADE,
        blank=False
    )

    specialist = ChainedForeignKey(
        Specialist,
        chained_field="salon",
        chained_model_field="salon",
        show_all=False,
        sort=True,
        on_delete=models.CASCADE,
        blank=True,
    )
    services = ChainedForeignKey(
        Service,
        chained_field="specialist",
        chained_model_field="services",
        show_all=False,
        sort=True,
        on_delete=models.CASCADE,
        blank=True,
    )

    @property
    def time(self):
        return self.TIMESLOT_LIST[self.timeslot][1]
