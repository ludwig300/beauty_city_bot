from django.contrib import admin

from .models import Salon, Specialist, Service, Schedule, User


class ScheduleServiceInline(admin.TabularInline):
    model = Schedule.service.through


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_time', 'salon',
                    'specialist',)
    ordering = ('date_time',)
    inlines = [
        ScheduleServiceInline,
    ]


admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(User)


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    raw_id_fields = ('services', 'salon')

