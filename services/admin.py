from django.contrib import admin

from .models import User, Salon, Service, Specialist, Schedule


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('salon', 'full_name')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('salon', 'specialist', 'services', 'user', 'date', 'time')


admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(User)
