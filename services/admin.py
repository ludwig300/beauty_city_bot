from django.contrib import admin

from .models import User, Salon, Service, Specialist, Schedule


class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('salon', 'full_name')


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('salon', 'specialist', 'services', 'user', 'date', 'time')


admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(User)
admin.site.register(Specialist, SpecialistAdmin)
