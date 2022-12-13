from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    full_name = models.CharField(
        'ФИО Пользователя',
        max_length=200,
        db_index=True
    )
    phoneNumber = PhoneNumberField(
        unique=True,
        null=False,
        blank=False
    )
    last_lat = models.FloatField('Широта', blank=True, null=True)
    last_lon = models.FloatField('Долгота', blank=True, null=True)

    def __str__(self):
        return self.full_name


class Salon(models.Model):
    name = models.CharField(
        'Наименование салона',
        max_length=200,
        db_index=True,
    )

    address = models.CharField(
        'Адрес Салона',
        max_length=200,
        blank=True,
        null=True)

    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)

    def __str__(self):
        return f'Салон {self.name} по адресу {self.address}'


class Service(models.Model):
    name = models.CharField(
        'Наименование услуги', max_length=200, db_index=True,
    )
    price = models.IntegerField('Цена услуги', db_index=True)

    def __str__(self):
        return f'Услуга: {self.name}. Цена: {self.price}.'


class Specialist(models.Model):
    name = models.CharField(
        'ФИО мастера',
        max_length=200,
        db_index=True,
    )

    service = models.ManyToManyField(
        Service, related_name="services",
        verbose_name='Услуги, оказываемые мастером',
        blank=True
    )

    def __str__(self):
        return f' Мастер {self.name}'


class ScheduleSpecInSalon(models.Model):
    date = models.DateField('Дата', blank=False)
    specialist = models.ForeignKey(
        Specialist,
        verbose_name='Мастер',
        on_delete=models.CASCADE,
        blank=False,
    )

    salon = models.ForeignKey(
        Salon,
        verbose_name='Салон',
        on_delete=models.CASCADE,
        blank=False,
    )

    def __str__(self):
        return f'{self.date} мастер {self.specialist} работает в салоне {self.salon}'


class TimeSlot(models.Model):
    free_time = models.TimeField('Свободное время', blank=False)


class Schedule(models.Model):
    order_datetime = models.DateTimeField(
        verbose_name='Дата и время регистрации на посещение',
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

    date = models.DateField('Дата посещения', help_text="YYYY-MM-DD")

    # timeslot = models.IntegerField(choices=TIMESLOT_LIST, null=True)

    service = models.ForeignKey(
        Service,
        verbose_name='Услуга',
        on_delete=models.CASCADE,
        blank=True,
    )

    timeslot = models.ForeignKey(
        TimeSlot,
        verbose_name='Промежуток времени',
        on_delete=models.CASCADE,
        blank=False
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

    def __str__(self):
        return f'Запись: {self.date} {self.timeslot} - {self.user} - {self.service} - {self.specialist} - {self.salon}'

    class Meta:
        # verbose_name = _("schedule")
        # verbose_name_plural = _("schedules")
        constraints = [
            models.UniqueConstraint(
                fields=['order_datetime', 'user', 'date', 'service', 'timeslot', 'specialist', 'salon'],
                name="unique_schedule_items"
            )
        ]