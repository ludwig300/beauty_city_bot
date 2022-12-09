from django.contrib import admin

from .models import User, Salon, PeriodOfTime, Service, Specialist, SpecialistInSalon, Schedule


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'phoneNumber',)


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('salon_name', 'address',)


@admin.register(PeriodOfTime)
class PeriodOfTimeAdmin(admin.ModelAdmin):
    list_display = ('start_period', 'end_period',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'price',)


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('specialist_name',)


@admin.register(SpecialistInSalon)
class SpecialistInSalonAdmin(admin.ModelAdmin):
    list_display = ('date', 'specialist', 'salon',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('date_service', 'time_service',)
