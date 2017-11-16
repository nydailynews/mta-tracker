from django.contrib import admin
from django.conf import settings
from mta.models import Mode, Line, DelayAlert

class ModeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    save_on_top = True
    prepopulated_fields = { 'slug': ('name',) }

class LineAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    save_on_top = True
    prepopulated_fields = { 'slug': ('name',) }

class DelayAlertAdmin(admin.ModelAdmin):
    pass

admin.site.register(Mode, ModeAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(DelayAlert, DelayAlertAdmin)
