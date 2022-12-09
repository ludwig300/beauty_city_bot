from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
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


class PeriodOfTime(models.Model):
    start_period = models.TimeField('Время начала', blank=False,)
    end_period = models.TimeField('Время завершения', blank=False,)

    def __str__(self):
        return f'{self.start_period} - {self.end_period}'


class Service(models.Model):
    service_name = models.CharField(
        'Наименование услуги', max_length=200, db_index=True,
    )
    price = models.IntegerField('Цена услуги', db_index=True)

    def __str__(self):
        return self.service_name


class Specialist(models.Model):
    specialist_name = models.CharField(
        'ФИО Специалиста',
        max_length=200,
        db_index=True,
    )
    salon = models.ManyToManyField(
        Salon,
        verbose_name='Салоны, в которых работает Мастер',
        related_name="salons",
        blank=True,
    )
    service = models.ManyToManyField(
        Service,
        verbose_name='Услуги, оказываемые Мастером',
        related_name="services",
        blank=True,
    )

    def __str__(self):
        return f'Мастер: {self.specialist_name}'


class SpecialistInSalon(models.Model):
    date = models.DateField('Дата работы', blank=True)
    specialist = models.ForeignKey(
        Specialist,
        verbose_name='Имя мастера',
        on_delete=models.CASCADE,
        blank=False,
    )
    salon = models.ForeignKey(
        Salon,
        verbose_name='в каком салоне работает',
        on_delete=models.CASCADE,
        blank=False,
    )

    def __str__(self):
        return f'{self.date} - Мастер {self.specialist} работает в салоне {self.salon}'


class Schedule(models.Model):
    order_datetime = models.DateTimeField(
        'Дата и время регистрации на посещение',
        auto_now=True,
        blank=False,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Имя клиента',
        on_delete=models.CASCADE,
        related_name='schedules_user',
        blank=False,
    )
    date_service = models.DateField(
        verbose_name='Дата записи',
        blank=False,
    )
    time_service = models.ForeignKey(
        PeriodOfTime,
        verbose_name='Время записи',
        on_delete=models.CASCADE,
        blank=False,
    )
    service = models.ForeignKey(
        Service,
        verbose_name='Услуга',
        on_delete=models.CASCADE,
        blank=True,
    )
    specialist = models.ForeignKey(
        Specialist,
        verbose_name='Мастер',
        on_delete=models.CASCADE,
        blank=True,
    )
    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон',
        on_delete=models.CASCADE,
        blank=False
    )

    def __unicode__(self):
        return f'{self.order_datetime}: {self.user} - {self.date_service} {self.time_service} - {self.service} - ' \
               f'мастер: {self.specialist} в салоне {self.salon}'
